import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables"""

    # Database
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "smart_traffic_bandung")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))

    # API
    BANDUNG_API_URL: str = os.getenv(
        "BANDUNG_API_URL", "https://pelindung.bandung.go.id:8443/api/cek"
    )
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # AI
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))
    VEHICLE_CLASSES: list = ["car", "motorcycle", "bus", "truck"]

    # Traffic Status Thresholds
    LANCAR_THRESHOLD: int = int(os.getenv("LANCAR_THRESHOLD", 40))
    PADAT_THRESHOLD: int = int(os.getenv("PADAT_THRESHOLD", 70))

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()
