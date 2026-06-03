from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.schemas import TrafficStatus, TrafficAnalysisCreate
from app.services.database_service import db_service
from app.services.cctv_service import cctv_service
from app.ai.yolo_detector import yolo_detector
from app.mock_data import MOCK_ANALYSIS
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Traffic Analysis"])


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


@router.get("/{cctv_id}", response_model=TrafficStatus)
async def analyze_traffic(cctv_id: str, db: Optional[Session] = Depends(get_db)):
    """
    Analyze traffic dari CCTV tertentu menggunakan YOLO
    
    Args:
        cctv_id: CCTV ID
        
    Returns:
        Traffic status dengan vehicle count dan status (LANCAR/PADAT/MACET)
    """
    try:
        logger.info(f"=== Analyze traffic untuk CCTV ID: {cctv_id} ===")
        cctv = None
        
        # Get CCTV data dari database jika tersedia
        if db:
            try:
                cctv = db_service.get_cctv_by_id(db, cctv_id)
                if cctv:
                    logger.info(f"Found CCTV in DB: {cctv}")
            except Exception as e:
                logger.error(f"Error getting CCTV from database: {str(e)}")
        
        # Get dari API jika tidak ada di database
        if not cctv:
            try:
                cctv_data = await cctv_service.fetch_cctv_by_id(cctv_id)
                if cctv_data:
                    logger.info(f"Found CCTV from API: {cctv_data}")
                    cctv = cctv_data
            except Exception as e:
                logger.warning(f"Error getting CCTV from API: {str(e)}")
        
        # Check cache - jika ada analysis dalam 30 detik terakhir, return itu
        if db:
            try:
                latest_analysis = db_service.get_latest_analysis(db, cctv_id)
                if latest_analysis:
                    time_diff = (datetime.utcnow() - latest_analysis.created_at).total_seconds()
                    if time_diff < 3:  # Cache hanya 3 detik - minimal caching
                        logger.info(f"Using cached analysis for {cctv_id}")
                        return TrafficStatus(
                            cctv_name=latest_analysis.cctv_name,
                            cctv_id=cctv_id,
                            vehicle_count=latest_analysis.vehicle_count,
                            status=latest_analysis.status,
                            car_count=latest_analysis.car_count,
                            motorcycle_count=latest_analysis.motorcycle_count,
                            bus_count=latest_analysis.bus_count,
                            truck_count=latest_analysis.truck_count,
                            confidence_score=latest_analysis.confidence_score,
                            timestamp=latest_analysis.created_at,
                        )
            except Exception as e:
                logger.error(f"Error checking cache: {str(e)}")

        # Check mock data (fallback untuk testing)
        if cctv_id in MOCK_ANALYSIS:
            mock_data = MOCK_ANALYSIS[cctv_id]
            return TrafficStatus(
                cctv_name=mock_data["cctv_name"],
                cctv_id=cctv_id,
                vehicle_count=mock_data["vehicle_count"],
                status=mock_data["status"],
                car_count=mock_data["car_count"],
                motorcycle_count=mock_data["motorcycle_count"],
                bus_count=mock_data["bus_count"],
                truck_count=mock_data["truck_count"],
                confidence_score=mock_data["confidence_score"],
                timestamp=datetime.utcnow(),
            )

        # Jika CCTV tidak ditemukan, return error
        if not cctv:
            logger.error(f"CCTV {cctv_id} not found di database maupun API")
            raise HTTPException(status_code=404, detail=f"CCTV {cctv_id} tidak ditemukan")

        # Process traffic analysis
        stream_url = cctv.get("stream_cctv") or cctv.get("stream_url") if isinstance(cctv, dict) else cctv.stream_url
        logger.info(f"Processing stream: {stream_url}")
        
        detection_result = await yolo_detector.detect_vehicles_from_stream(
            stream_url,
            frame_interval=2,
            max_frames=10,
        )

        # Save ke database jika tersedia
        if db:
            try:
                analysis_data = TrafficAnalysisCreate(
                    cctv_id=cctv_id,
                    cctv_name=cctv.get("cctv_name") if isinstance(cctv, dict) else cctv.cctv_name,
                    vehicle_count=detection_result["vehicle_count"],
                    car_count=detection_result["car_count"],
                    motorcycle_count=detection_result["motorcycle_count"],
                    bus_count=detection_result["bus_count"],
                    truck_count=detection_result["truck_count"],
                    status=detection_result["status"],
                    confidence_score=detection_result["confidence_score"],
                )
                saved_analysis = db_service.save_traffic_analysis(db, analysis_data)
                
                result = TrafficStatus(
                    cctv_name=saved_analysis.cctv_name,
                    cctv_id=cctv_id,
                    vehicle_count=saved_analysis.vehicle_count,
                    status=saved_analysis.status,
                    car_count=saved_analysis.car_count,
                    motorcycle_count=saved_analysis.motorcycle_count,
                    bus_count=saved_analysis.bus_count,
                    truck_count=saved_analysis.truck_count,
                    confidence_score=saved_analysis.confidence_score,
                    timestamp=saved_analysis.created_at,
                )
                logger.info(f"=== Returning analysis: {result.cctv_id} ({result.cctv_name}) ===")
                return result
            except Exception as e:
                logger.error(f"Error saving analysis to database: {str(e)}")
                # Tetap return hasil meski gagal save
        
        # Return tanpa database
        cctv_name = cctv.get("cctv_name") if isinstance(cctv, dict) else cctv.cctv_name
        return TrafficStatus(
            cctv_name=cctv_name,
            cctv_id=cctv_id,
            vehicle_count=detection_result["vehicle_count"],
            status=detection_result["status"],
            car_count=detection_result["car_count"],
            motorcycle_count=detection_result["motorcycle_count"],
            bus_count=detection_result["bus_count"],
            truck_count=detection_result["truck_count"],
            confidence_score=detection_result["confidence_score"],
            timestamp=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing traffic: {str(e)}")


@router.get("/history/{cctv_id}", response_model=List[TrafficStatus])
async def get_analysis_history(
    cctv_id: str,
    hours: int = 24,
    db: Optional[Session] = Depends(get_db),
):
    """
    Get traffic analysis history untuk CCTV tertentu
    
    Args:
        cctv_id: CCTV ID
        hours: Berapa jam history yang diambil (default: 24 jam)
        
    Returns:
        List traffic analysis history
    """
    try:
        if not db:
            logger.warning("Database not available, returning empty history")
            return []
        
        analyses = db_service.get_analysis_history(db, cctv_id, hours)
        
        return [
            TrafficStatus(
                cctv_name=a.cctv_name,
                cctv_id=a.cctv_id,
                vehicle_count=a.vehicle_count,
                status=a.status,
                car_count=a.car_count,
                motorcycle_count=a.motorcycle_count,
                bus_count=a.bus_count,
                truck_count=a.truck_count,
                confidence_score=a.confidence_score,
                timestamp=a.created_at,
            )
            for a in analyses
        ]

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return []


@router.get("/latest", response_model=List[TrafficStatus])
async def get_latest_analysis(db: Optional[Session] = Depends(get_db)):
    """
    Get latest traffic analysis untuk semua CCTV
    
    Returns:
        List latest traffic status untuk semua CCTV
    """
    try:
        if not db:
            logger.warning("Database not available, returning mock analysis")
            # Return mock data jika database tidak tersedia
            result = []
            for cctv_id, mock_data in MOCK_ANALYSIS.items():
                result.append(TrafficStatus(
                    cctv_name=mock_data["cctv_name"],
                    cctv_id=cctv_id,
                    vehicle_count=mock_data["vehicle_count"],
                    status=mock_data["status"],
                    car_count=mock_data["car_count"],
                    motorcycle_count=mock_data["motorcycle_count"],
                    bus_count=mock_data["bus_count"],
                    truck_count=mock_data["truck_count"],
                    confidence_score=mock_data["confidence_score"],
                    timestamp=datetime.utcnow(),
                ))
            return result
        
        analyses = db_service.get_all_latest_analysis(db)
        
        return [
            TrafficStatus(
                cctv_name=a.cctv_name,
                cctv_id=a.cctv_id,
                vehicle_count=a.vehicle_count,
                status=a.status,
                car_count=a.car_count,
                motorcycle_count=a.motorcycle_count,
                bus_count=a.bus_count,
                truck_count=a.truck_count,
                confidence_score=a.confidence_score,
                timestamp=a.created_at,
            )
            for a in analyses
        ]

    except Exception as e:
        logger.error(f"Error getting latest analysis: {str(e)}")
        # Return mock data pada error
        result = []
        for cctv_id, mock_data in MOCK_ANALYSIS.items():
            result.append(TrafficStatus(
                cctv_name=mock_data["cctv_name"],
                cctv_id=cctv_id,
                vehicle_count=mock_data["vehicle_count"],
                status=mock_data["status"],
                car_count=mock_data["car_count"],
                motorcycle_count=mock_data["motorcycle_count"],
                bus_count=mock_data["bus_count"],
                truck_count=mock_data["truck_count"],
                confidence_score=mock_data["confidence_score"],
                timestamp=datetime.utcnow(),
            ))
        return result
    """
    Analyze traffic dari CCTV tertentu menggunakan YOLO
    
    Args:
        cctv_id: CCTV ID
        
    Returns:
        Traffic status dengan vehicle count dan status (LANCAR/PADAT/MACET)
    """
    try:
        # Get CCTV data
        cctv = db_service.get_cctv_by_id(db, cctv_id)
        if not cctv:
            raise HTTPException(status_code=404, detail="CCTV not found")

        # Check cache - jika ada analysis dalam 30 detik terakhir, return itu
        latest_analysis = db_service.get_latest_analysis(db, cctv_id)
        if latest_analysis:
            time_diff = (datetime.utcnow() - latest_analysis.created_at).total_seconds()
            if time_diff < 30:  # Cache 30 detik
                return TrafficStatus(
                    cctv_name=latest_analysis.cctv_name,
                    cctv_id=cctv_id,
                    vehicle_count=latest_analysis.vehicle_count,
                    status=latest_analysis.status,
                    car_count=latest_analysis.car_count,
                    motorcycle_count=latest_analysis.motorcycle_count,
                    bus_count=latest_analysis.bus_count,
                    truck_count=latest_analysis.truck_count,
                    confidence_score=latest_analysis.confidence_score,
                    timestamp=latest_analysis.created_at,
                )

        # Process traffic analysis
        logger.info(f"Processing stream: {cctv.stream_url}")
        
        detection_result = await yolo_detector.detect_vehicles_from_stream(
            cctv.stream_url,
            frame_interval=2,
            max_frames=10,
        )

        # Save ke database
        analysis_data = TrafficAnalysisCreate(
            cctv_id=cctv_id,
            cctv_name=cctv.cctv_name,
            vehicle_count=detection_result["vehicle_count"],
            car_count=detection_result["car_count"],
            motorcycle_count=detection_result["motorcycle_count"],
            bus_count=detection_result["bus_count"],
            truck_count=detection_result["truck_count"],
            status=detection_result["status"],
            confidence_score=detection_result["confidence_score"],
        )
        
        saved_analysis = db_service.save_traffic_analysis(db, analysis_data)

        return TrafficStatus(
            cctv_name=cctv.cctv_name,
            cctv_id=cctv_id,
            vehicle_count=saved_analysis.vehicle_count,
            status=saved_analysis.status,
            car_count=saved_analysis.car_count,
            motorcycle_count=saved_analysis.motorcycle_count,
            bus_count=saved_analysis.bus_count,
            truck_count=saved_analysis.truck_count,
            confidence_score=saved_analysis.confidence_score,
            timestamp=saved_analysis.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing traffic: {str(e)}")


@router.get("/history/{cctv_id}", response_model=List[TrafficStatus])
async def get_analysis_history(
    cctv_id: str,
    hours: int = 24,
    db: Session = Depends(get_db),
):
    """
    Get traffic analysis history untuk CCTV tertentu
    
    Args:
        cctv_id: CCTV ID
        hours: Berapa jam history yang diambil (default: 24 jam)
        
    Returns:
        List traffic analysis history
    """
    try:
        analyses = db_service.get_analysis_history(db, cctv_id, hours)
        
        return [
            TrafficStatus(
                cctv_name=a.cctv_name,
                cctv_id=a.cctv_id,
                vehicle_count=a.vehicle_count,
                status=a.status,
                car_count=a.car_count,
                motorcycle_count=a.motorcycle_count,
                bus_count=a.bus_count,
                truck_count=a.truck_count,
                confidence_score=a.confidence_score,
                timestamp=a.created_at,
            )
            for a in analyses
        ]

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting history")


@router.get("/latest", response_model=List[TrafficStatus])
async def get_latest_analysis(db: Session = Depends(get_db)):
    """
    Get latest traffic analysis untuk semua CCTV
    
    Returns:
        List latest traffic status untuk semua CCTV
    """
    try:
        analyses = db_service.get_all_latest_analysis(db)
        
        return [
            TrafficStatus(
                cctv_name=a.cctv_name,
                cctv_id=a.cctv_id,
                vehicle_count=a.vehicle_count,
                status=a.status,
                car_count=a.car_count,
                motorcycle_count=a.motorcycle_count,
                bus_count=a.bus_count,
                truck_count=a.truck_count,
                confidence_score=a.confidence_score,
                timestamp=a.created_at,
            )
            for a in analyses
        ]

    except Exception as e:
        logger.error(f"Error getting latest analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting latest analysis")