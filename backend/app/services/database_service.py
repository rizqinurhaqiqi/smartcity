from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base, CCTV, TrafficAnalysis
from app.models.schemas import TrafficAnalysisCreate, CCTV as CCTVSchema
from app.config import settings
import logging
from typing import List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service untuk database operations"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize database connection dan create tables"""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")

    def get_session(self) -> Session:
        """Get database session"""
        if self.SessionLocal is None:
            logger.error("Database not initialized - SessionLocal is None")
            return None
        return self.SessionLocal()

    # CCTV Methods
    def save_cctv(self, session: Session, cctv_data: dict) -> CCTV:
        """Save or update CCTV data"""
        try:
            existing = session.query(CCTV).filter(
                CCTV.cctv_id == cctv_data["id"]
            ).first()

            if existing:
                existing.cctv_name = cctv_data["cctv_name"]
                existing.lat = cctv_data["lat"]
                existing.lng = cctv_data["lng"]
                existing.stream_url = cctv_data["stream_cctv"]
                existing.dinas = cctv_data.get("dinas", "")
                existing.updated_at = datetime.utcnow()
            else:
                existing = CCTV(
                    cctv_id=cctv_data["id"],
                    cctv_name=cctv_data["cctv_name"],
                    lat=cctv_data["lat"],
                    lng=cctv_data["lng"],
                    stream_url=cctv_data["stream_cctv"],
                    dinas=cctv_data.get("dinas", ""),
                )
                session.add(existing)

            session.commit()
            return existing
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving CCTV: {str(e)}")
            raise

    def get_all_cctvs(self, session: Session) -> List[CCTV]:
        """Get all CCTV from database"""
        try:
            return session.query(CCTV).all()
        except Exception as e:
            logger.error(f"Error getting all CCTVs: {str(e)}")
            return []

    def get_cctv_by_id(self, session: Session, cctv_id: str) -> Optional[CCTV]:
        """Get CCTV by ID"""
        try:
            return session.query(CCTV).filter(CCTV.cctv_id == cctv_id).first()
        except Exception as e:
            logger.error(f"Error getting CCTV by ID: {str(e)}")
            return None

    # Traffic Analysis Methods
    def save_traffic_analysis(
        self, session: Session, analysis_data: TrafficAnalysisCreate
    ) -> TrafficAnalysis:
        """Save traffic analysis result"""
        try:
            analysis = TrafficAnalysis(
                cctv_id=analysis_data.cctv_id,
                cctv_name=analysis_data.cctv_name,
                vehicle_count=analysis_data.vehicle_count,
                car_count=analysis_data.car_count,
                motorcycle_count=analysis_data.motorcycle_count,
                bus_count=analysis_data.bus_count,
                truck_count=analysis_data.truck_count,
                status=analysis_data.status,
                confidence_score=analysis_data.confidence_score,
                frame_timestamp=datetime.utcnow(),
            )
            session.add(analysis)
            session.commit()
            return analysis
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving traffic analysis: {str(e)}")
            raise

    def get_latest_analysis(self, session: Session, cctv_id: str) -> Optional[TrafficAnalysis]:
        """Get latest traffic analysis for specific CCTV"""
        try:
            return (
                session.query(TrafficAnalysis)
                .filter(TrafficAnalysis.cctv_id == cctv_id)
                .order_by(desc(TrafficAnalysis.created_at))
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting latest analysis: {str(e)}")
            return None

    def get_analysis_history(
        self, session: Session, cctv_id: str, hours: int = 24
    ) -> List[TrafficAnalysis]:
        """Get analysis history for specific CCTV"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            return (
                session.query(TrafficAnalysis)
                .filter(TrafficAnalysis.cctv_id == cctv_id)
                .filter(TrafficAnalysis.created_at >= since)
                .order_by(desc(TrafficAnalysis.created_at))
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting analysis history: {str(e)}")
            return []

    def get_all_latest_analysis(self, session: Session) -> List[TrafficAnalysis]:
        """Get latest analysis for all CCTVs"""
        try:
            # Subquery untuk get latest timestamp per CCTV
            from sqlalchemy.sql import func
            
            latest = (
                session.query(
                    TrafficAnalysis.cctv_id,
                    func.max(TrafficAnalysis.created_at).label("max_created"),
                )
                .group_by(TrafficAnalysis.cctv_id)
                .subquery()
            )

            return (
                session.query(TrafficAnalysis)
                .join(
                    latest,
                    (TrafficAnalysis.cctv_id == latest.c.cctv_id)
                    & (TrafficAnalysis.created_at == latest.c.max_created),
                )
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting all latest analysis: {str(e)}")
            return []


# Singleton instance
db_service = DatabaseService()