"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "QAtron Control Plane"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:80",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "postgresql://qatron:qatron@postgres:5432/qatron"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Celery (uses Redis as broker; optional for control-plane)
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    CELERY_ARTIFACT_RETENTION_DAYS: int = 30

    # S3/MinIO
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY_ID: str = "minioadmin"
    S3_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "qatron-artifacts"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # Default admin user (change in production)
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_V1_STR: str = "/api/v1"

    # Orchestrator (for triggering queued runs)
    ORCHESTRATOR_URL: str = "http://orchestrator:8001"

    # Internal API (orchestrator/worker); if set, requests must send X-Internal-Secret
    INTERNAL_API_SECRET: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
