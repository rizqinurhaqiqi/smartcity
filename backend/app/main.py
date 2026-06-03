from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import cctv, analysis, health
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Smart Traffic Bandung API",
        description="Real-time traffic monitoring system for Bandung using CCTV and AI",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(cctv.router)
    app.include_router(analysis.router)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Smart Traffic Bandung API",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info("FastAPI application created successfully")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        log_level="info",
    )
