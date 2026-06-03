from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.schemas import CCTV as CCTVSchema
from app.services.cctv_service import cctv_service
from app.services.database_service import db_service
from app.mock_data import MOCK_CCTVS
import logging
import httpx
from urllib.parse import quote

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


@router.get("", response_model=List[CCTVSchema])
async def get_all_cctv(db: Optional[Session] = Depends(get_db)):
    """
    Get semua CCTV dari API Bandung dan simpan ke database
    
    Returns:
        List of all CCTV dengan detail lokasi dan stream URL
    """
    try:
        # Fetch dari API Bandung
        cctvs_data = await cctv_service.fetch_all_cctv()
        
        if not cctvs_data:
            logger.warning("No CCTV data fetched from API, using mock data")
            # Fallback ke mock data jika API error
            return MOCK_CCTVS

        # Simpan ke database jika tersedia
        if db:
            saved_cctvs = []
            for cctv_data in cctvs_data:
                try:
                    saved_cctv = db_service.save_cctv(db, cctv_data)
                    saved_cctvs.append(saved_cctv)
                except Exception as e:
                    logger.error(f"Error saving CCTV {cctv_data.get('id')}: {str(e)}")
                    # Tetap return cctv_data meski gagal save
                    saved_cctvs.append(cctv_data)
            return saved_cctvs
        else:
            # Jika database tidak tersedia, return raw data
            logger.warning("Database not available, returning raw CCTV data")
            return cctvs_data

    except Exception as e:
        logger.error(f"Error in get_all_cctv: {str(e)}")
        # Fallback ke mock data sebagai last resort
        logger.warning("Returning mock CCTV data as fallback")
        return MOCK_CCTVS


@router.get("/{cctv_id}", response_model=CCTVSchema)
async def get_cctv_detail(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """
    Get detail CCTV by ID
    
    Args:
        cctv_id: CCTV ID
        
    Returns:
        CCTV detail dengan lokasi dan stream URL
    """
    try:
        # Try dari database dulu (jika tersedia)
        if db:
            cctv = db_service.get_cctv_by_id(db, cctv_id)
            if cctv:
                return cctv
        
        # Try fetch dari API
        cctv_data = await cctv_service.fetch_cctv_by_id(cctv_id)
        if cctv_data:
            if db:
                cctv = db_service.save_cctv(db, cctv_data)
                return cctv
            else:
                return cctv_data
        
        # Check mock data
        for mock_cctv in MOCK_CCTVS:
            if mock_cctv['id'] == cctv_id:
                return _cctv
        
        raise HTTPException(status_code=404, detail="CCTV not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_cctv_detail: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stream/test/{cctv_id}")
async def test_stream(cctv_id: str):
    """
    Test apakah stream URL accessible
    
    Args:
        cctv_id: CCTV ID
        
    Returns:
        Debug info tentang stream
    """
    try:
        # Get CCTV data
        cctv_data = await cctv_service.fetch_cctv_by_id(cctv_id)
        if not cctv_data:
            raise HTTPException(status_code=404, detail="CCTV not found")
        
        stream_url = cctv_data.get("stream_cctv") or cctv_data.get("stream_url")
        logger.info(f"Testing stream: {stream_url}")
        
        # Test accessibility
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
                    "content_length": response.headers.get("content-length", "unknown"),
                }
            except Exception as e:
                logger.error(f"Stream test error: {str(e)}")
                return {
                    "cctv_id": cctv_id,
                    "cctv_name": cctv_data.get("cctv_name"),
                    "stream_url": stream_url,
                    "accessible": False,
                    "error": str(e),
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{cctv_id}")
async def get_stream(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """
    Proxy stream dari eksternal source untuk bypass CORS
    
    Args:
        cctv_id: CCTV ID
        
    Returns:
        Stream content dengan CORS headers
    """
    try:
        logger.info(f"Getting stream for CCTV: {cctv_id}")
        
        # Get CCTV data
        cctv_data = None
        if db:
            try:
                cctv_data = db_service.get_cctv_by_id(db, cctv_id)
            except:
                pass
        
        if not cctv_data:
            cctv_data = await cctv_service.fetch_cctv_by_id(cctv_id)
        
        if not cctv_data:
            # Check mock data
            for mock_cctv in MOCK_CCTVS:
                if mock_cctv['id'] == cctv_id:
                    cctv_data = mock_cctv
                    break
        
        if not cctv_data:
            raise HTTPException(status_code=404, detail="CCTV not found")
        
        stream_url = cctv_data.get("stream_url") or cctv_data.get("stream_cctv")
        if not stream_url:
            raise HTTPException(status_code=400, detail="No stream URL for this CCTV")
        
        logger.info(f"Proxying stream from: {stream_url}")
        
        # Fetch stream dengan SSL bypass
        async with httpx.AsyncClient(verify=False, timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(stream_url)
                
                if response.status_code >= 400:
                    raise HTTPException(status_code=response.status_code, detail="Cannot access stream")
                
                # Return dengan CORS headers
                return StreamingResponse(
                    iter([response.content]),
                    status_code=200,
                    headers={
                        "Content-Type": response.headers.get("content-type", "application/octet-stream"),
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Range",
                        "Cache-Control": "public, max-age=3600",
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Error fetching stream: {str(e)}")
                raise HTTPException(status_code=502, detail=f"Cannot connect to stream: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream-manifest/{cctv_id}")
async def get_stream_manifest(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """
    Proxy HLS manifest (.m3u8) dan rewrite URLs untuk point ke proxy
    
    Args:
        cctv_id: CCTV ID
        
    Returns:
        Modified manifest dengan proxy URLs
    """
    try:
        logger.info(f"Getting stream manifest for CCTV: {cctv_id}")
        
        # Get CCTV data
        cctv_data = None
        if db:
            try:
                cctv_data = db_service.get_cctv_by_id(db, cctv_id)
            except:
                pass
        
        if not cctv_data:
            cctv_data = await cctv_service.fetch_cctv_by_id(cctv_id)
        
        if not cctv_data:
            for mock_cctv in MOCK_CCTVS:
                if mock_cctv['id'] == cctv_id:
                    cctv_data = mock_cctv
                    break
        
        if not cctv_data:
            raise HTTPException(status_code=404, detail="CCTV not found")
        
        stream_url = cctv_data.get("stream_url") or cctv_data.get("stream_cctv")
        if not stream_url:
            raise HTTPException(status_code=400, detail="No stream URL for this CCTV")
        
        logger.info(f"Fetching manifest from: {stream_url}")
        
        # Fetch manifest
        async with httpx.AsyncClient(verify=False, timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(stream_url)
                
                if response.status_code >= 400:
                    raise HTTPException(status_code=response.status_code, detail="Cannot access manifest")
                
                manifest = response.text
                
                # Rewrite URLs dalam manifest untuk point ke proxy
                # Jika URL relative, resolve ke base URL
                from urllib.parse import urljoin
                base_url = "/".join(stream_url.split("/")[:-1])
                
                lines = manifest.split("\n")
                modified_lines = []
                
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        # Ini adalah segment URL
                        segment_url = urljoin(stream_url, line.strip())
                        # Proxy segment via backend
                        encoded_url = quote(segment_url, safe='')
                        proxied_url = f"/cctv/segment-proxy?url={encoded_url}"
                        modified_lines.append(proxied_url)
                    else:
                        modified_lines.append(line)
                
                modified_manifest = "\n".join(modified_lines)
                logger.info(f"Manifest modified, {len(lines)} lines processed")
                
                return StreamingResponse(
                    iter([modified_manifest.encode()]),
                    status_code=200,
                    headers={
                        "Content-Type": "application/vnd.apple.mpegurl",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Cache-Control": "no-cache",
                    }
                )
            except httpx.RequestError as e:
                logger.error(f"Error fetching manifest: {str(e)}")
                raise HTTPException(status_code=502, detail=f"Cannot connect to stream: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stream_manifest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segment-proxy")
async def get_segment(url: str):
    """
    Proxy HLS segments dengan CORS headers
    
    Args:
        url: Segment URL (encoded)
        
    Returns:
        Segment content
    """
    try:
        logger.debug(f"Proxying segment: {url[:80]}...")
        
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(url)
            
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail="Cannot access segment")
            
            return StreamingResponse(
                iter([response.content]),
                status_code=200,
                headers={
                    "Content-Type": response.headers.get("content-type", "video/mp2t"),
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600",
                }
            )
    except httpx.RequestError as e:
        logger.error(f"Error fetching segment: {str(e)}")
        raise HTTPException(status_code=502, detail="Cannot access segment")
    except Exception as e:
        logger.error(f"Error in get_segment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))