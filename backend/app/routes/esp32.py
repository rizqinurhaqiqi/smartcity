from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.ai.yolo_detector import yolo_detector
from app.config import settings
from datetime import datetime
import logging
import asyncio
import aiohttp
import threading
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/esp32", tags=["ESP32"])

# ─────────────────────────────────────────────
# In-memory store: hasil analisis terakhir
# ─────────────────────────────────────────────
_latest_result: Dict[str, Any] = {
    "vehicle_count": 0,
    "car_count": 0,
    "motorcycle_count": 0,
    "bus_count": 0,
    "truck_count": 0,
    "status": "UNKNOWN",
    "confidence_score": 0.0,
    "timestamp": None,
    "source": "hp_camera",
}

_auto_fetch_enabled = True
_fetch_thread = None


def _fetch_and_analyze():
    """
    Background thread: ambil frame dari HP Camera setiap 10 detik,
    jalankan YOLO, simpan hasilnya.
    ESP32 tinggal poll /esp32/result.
    """
    global _latest_result

    hp_url = f"http://{settings.HP_CAMERA_IP}:{settings.HP_CAMERA_PORT}/shot.jpg"
    interval = 1  # detik

    logger.info(f"[AutoFetch] Mulai auto-fetch dari {hp_url} setiap {interval} detik")

    while _auto_fetch_enabled:
        try:
            import requests
            import cv2
            import numpy as np

            resp = requests.get(hp_url, timeout=5)
            if resp.status_code == 200 and len(resp.content) > 1000:
                jpeg_bytes = resp.content
                logger.info(f"[AutoFetch] Frame diterima: {len(jpeg_bytes)} bytes")

                # Run YOLO detection
                nparr = np.frombuffer(jpeg_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    detection = yolo_detector._detect_vehicles_in_frame(frame)
                    vehicles = detection["vehicles"]
                    total = detection["total_count"]
                    conf = detection["avg_confidence"]

                    _latest_result = {
                        "vehicle_count": total,
                        "car_count": vehicles["car"],
                        "motorcycle_count": vehicles["motorcycle"],
                        "bus_count": vehicles["bus"],
                        "truck_count": vehicles["truck"],
                        "status": yolo_detector._determine_status(total),
                        "confidence_score": float(conf),
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "hp_camera",
                    }

                    logger.info(
                        f"[AutoFetch] Hasil: {total} kendaraan "
                        f"({vehicles['car']}M {vehicles['motorcycle']}Mtr) "
                        f"- {_latest_result['status']}"
                    )
                else:
                    logger.warning("[AutoFetch] Gagal decode frame dari HP camera")
            else:
                logger.warning(f"[AutoFetch] HP camera tidak merespons: HTTP {resp.status_code}")

        except requests.exceptions.ConnectionError:
            logger.warning(f"[AutoFetch] Tidak bisa connect ke HP camera {hp_url}")
        except Exception as e:
            logger.error(f"[AutoFetch] Error: {str(e)}")

        time.sleep(interval)


def _ensure_auto_fetch():
    """Start background thread jika belum jalan."""
    global _fetch_thread
    if _fetch_thread is None or not _fetch_thread.is_alive():
        _fetch_thread = threading.Thread(target=_fetch_and_analyze, daemon=True)
        _fetch_thread.start()
        logger.info("[AutoFetch] Background thread started")


# Start auto-fetch saat module di-import
_ensure_auto_fetch()


# ─────────────────────────────────────────────
#  ESP32 endpoints
# ─────────────────────────────────────────────

@router.post("/analyze")
async def analyze_from_esp32(request: Request):
    """
    Endpoint untuk menerima gambar JPEG dari ESP32 (opsional).
    Sekarang backend sudah auto-fetch dari HP camera,
    jadi ESP32 tidak perlu kirim gambar lagi.
    Tapi endpoint ini tetap ada untuk backward compatibility.
    """
    global _latest_result
    try:
        content_type = request.headers.get("content-type", "")
        jpeg_bytes = await request.body()

        if not jpeg_bytes or len(jpeg_bytes) == 0:
            raise HTTPException(status_code=400, detail="Body gambar kosong")

        logger.info(f"Menerima gambar dari ESP32: {len(jpeg_bytes)} bytes")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: yolo_detector._process_jpeg_bytes(jpeg_bytes)
        )

        _latest_result = {
            **result,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "esp32",
        }

        return _latest_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error menganalisis gambar dari ESP32: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gagal menganalisis: {str(e)}")


@router.get("/result")
async def get_latest_result():
    """
    Ambil hasil analisis terakhir.
    Di-polling oleh ESP32 untuk ditampilkan di LCD.
    """
    return _latest_result


@router.get("/status")
async def get_esp32_status():
    """Status endpoint."""
    return {
        "status": "OK",
        "message": "Backend aktif - auto-fetch dari HP camera",
        "auto_fetch": _auto_fetch_enabled,
        "hp_camera": f"http://{settings.HP_CAMERA_IP}:{settings.HP_CAMERA_PORT}",
        "last_analysis": _latest_result.get("timestamp"),
        "last_vehicle_count": _latest_result.get("vehicle_count", 0),
        "last_traffic_status": _latest_result.get("status", "UNKNOWN"),
        "yolo_model": yolo_detector.model_name,
        "server_time": datetime.utcnow().isoformat(),
    }


@router.post("/toggle-fetch")
async def toggle_auto_fetch():
    """Toggle auto-fetch on/off."""
    global _auto_fetch_enabled
    _auto_fetch_enabled = not _auto_fetch_enabled
    if _auto_fetch_enabled:
        _ensure_auto_fetch()
    return {"auto_fetch": _auto_fetch_enabled}
