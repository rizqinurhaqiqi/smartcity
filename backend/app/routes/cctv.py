from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.schemas import CCTV as CCTVSchema
from app.services.cctv_service import cctv_service
from app.services.database_service import db_service
from app.mock_data import MOCK_CCTVS
import logging
import httpx
from urllib.parse import quote, urljoin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cctv", tags=["CCTV"])


def get_db():
    """Get database session with fallback - safely handles exceptions"""
    db = None
    try:
        db = db_service.get_session()
        if db is None:
            logger.warning("Database session is None")
    except Exception as e:
        logger.error(f"Error getting database session: {str(e)}")
        db = None

    try:
        yield db
    finally:
        try:
            if db is not None and hasattr(db, 'close'):
                db.close()
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")


async def _get_cctv_data(cctv_id: str, db) -> Optional[dict]:
    """Helper: cari CCTV dari DB → API → mock data"""
    # 1. Coba dari database
    if db:
        try:
            cctv = db_service.get_cctv_by_id(db, cctv_id)
            if cctv:
                return cctv
        except Exception:
            pass

    # 2. Coba dari API Bandung
    try:
        cctv = await cctv_service.fetch_cctv_by_id(cctv_id)
        if cctv:
            return cctv
    except Exception:
        pass

    # 3. Fallback ke mock data
    for mock in MOCK_CCTVS:
        if mock['id'] == cctv_id:
            return mock

    return None


# ─────────────────────────────────────────────────────────────────
# PENTING: Route statis harus didefinisikan SEBELUM route /{cctv_id}
# agar FastAPI tidak salah routing!
# ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[CCTVSchema])
async def get_all_cctv(db: Optional[Session] = Depends(get_db)):
    """Get semua CCTV dari API Bandung"""
    try:
        cctvs_data = await cctv_service.fetch_all_cctv()

        if not cctvs_data:
            logger.warning("No CCTV data fetched from API, using mock data")
            return MOCK_CCTVS

        if db:
            saved = []
            for cctv_data in cctvs_data:
                try:
                    saved.append(db_service.save_cctv(db, cctv_data))
                except Exception as e:
                    logger.error(f"Error saving CCTV {cctv_data.get('id')}: {e}")
                    saved.append(cctv_data)
            return saved

        return cctvs_data

    except Exception as e:
        logger.error(f"Error in get_all_cctv: {e}")
        return MOCK_CCTVS


# ── STATIC ROUTES (harus sebelum /{cctv_id}) ──────────────────────

@router.get("/segment-proxy")
async def get_segment(url: str = Query(...)):
    """
    Proxy satu HLS segment (.ts) dengan CORS headers.
    Dipanggil oleh hls.js ketika memutar stream.
    """
    try:
        logger.debug(f"Proxying segment: {url[:80]}...")
        async with httpx.AsyncClient(verify=False, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Cannot access segment (upstream {response.status_code})"
                )

            return StreamingResponse(
                iter([response.content]),
                status_code=200,
                headers={
                    "Content-Type": response.headers.get("content-type", "video/mp2t"),
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=60",
                }
            )
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.error(f"Error fetching segment: {e}")
        raise HTTPException(status_code=502, detail=f"Cannot access segment: {e}")
    except Exception as e:
        logger.error(f"Error in get_segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream-manifest/{cctv_id}")
async def get_stream_manifest(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """
    Proxy HLS manifest (.m3u8) dan rewrite segment URLs agar melewati /segment-proxy.
    Ini diperlukan untuk menghindari CORS error saat browser langsung akses CCTV server.
    """
    try:
        cctv_data = await _get_cctv_data(cctv_id, db)
        if not cctv_data:
            raise HTTPException(status_code=404, detail="CCTV not found")

        stream_url = (
            cctv_data.get("stream_cctv")
            or cctv_data.get("stream_url")
            or (cctv_data.stream_url if hasattr(cctv_data, 'stream_url') else None)
        )
        if not stream_url:
            raise HTTPException(status_code=400, detail="No stream URL for this CCTV")

        logger.info(f"Fetching manifest: {stream_url}")

        async with httpx.AsyncClient(verify=False, timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(stream_url)

                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Cannot access manifest"
                    )

                manifest = response.text

                # Rewrite setiap baris segment URL → /cctv/segment-proxy?url=<encoded>
                lines = manifest.split("\n")
                modified = []
                for line in lines:
                    stripped = line.strip()
                    # Baris segment: tidak mulai dengan # dan tidak kosong
                    if stripped and not stripped.startswith("#"):
                        # Resolve relative URL ke absolute
                        abs_url = urljoin(stream_url, stripped)
                        encoded = quote(abs_url, safe='')
                        modified.append(f"/cctv/segment-proxy?url={encoded}")
                    else:
                        modified.append(line)

                modified_manifest = "\n".join(modified)
                logger.info(f"Manifest rewritten, {len(lines)} lines processed")

                return PlainTextResponse(
                    content=modified_manifest,
                    status_code=200,
                    headers={
                        "Content-Type": "application/vnd.apple.mpegurl",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Cache-Control": "no-cache, no-store",
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Error fetching manifest: {e}")
                raise HTTPException(status_code=502, detail=f"Cannot connect to stream: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stream_manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{cctv_id}")
async def get_stream(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """Proxy raw stream content (fallback untuk non-HLS)"""
    try:
        cctv_data = await _get_cctv_data(cctv_id, db)
        if not cctv_data:
            raise HTTPException(status_code=404, detail="CCTV not found")

        stream_url = (
            cctv_data.get("stream_url")
            or cctv_data.get("stream_cctv")
            or (cctv_data.stream_url if hasattr(cctv_data, 'stream_url') else None)
        )
        if not stream_url:
            raise HTTPException(status_code=400, detail="No stream URL for this CCTV")

        async with httpx.AsyncClient(verify=False, timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(stream_url)

                if response.status_code >= 400:
                    raise HTTPException(status_code=response.status_code, detail="Cannot access stream")

                return StreamingResponse(
                    iter([response.content]),
                    status_code=200,
                    headers={
                        "Content-Type": response.headers.get("content-type", "application/octet-stream"),
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "no-cache",
                    }
                )
            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=f"Cannot connect to stream: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/test/{cctv_id}")
async def test_stream(cctv_id: str):
    """Test apakah stream URL CCTV bisa diakses"""
    try:
        cctv_data = await cctv_service.fetch_cctv_by_id(cctv_id)
        if not cctv_data:
            raise HTTPException(status_code=404, detail="CCTV not found")

        stream_url = cctv_data.get("stream_cctv") or cctv_data.get("stream_url")

        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            try:
                response = await client.head(stream_url)
                return {
                    "cctv_id": cctv_id,
                    "cctv_name": cctv_data.get("cctv_name"),
                    "stream_url": stream_url,
                    "accessible": response.status_code < 400,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", "unknown"),
                }
            except Exception as e:
                return {
                    "cctv_id": cctv_id,
                    "stream_url": stream_url,
                    "accessible": False,
                    "error": str(e),
                }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── PARAMETERIZED ROUTE — harus paling bawah ──────────────────────

@router.get("/{cctv_id}", response_model=CCTVSchema)
async def get_cctv_detail(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """Get detail CCTV by ID"""
    try:
        cctv = await _get_cctv_data(cctv_id, db)
        if cctv:
            return cctv
        raise HTTPException(status_code=404, detail="CCTV not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_cctv_detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")