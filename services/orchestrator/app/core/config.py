"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "QAtron Orchestrator"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    # Database
    DATABASE_URL: str = "postgresql://qatron:qatron@postgres:5432/qatron"

    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # S3/MinIO
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY_ID: str = "minioadmin"
    S3_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "qatron-artifacts"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # Control Plane API
    CONTROL_PLANE_API_URL: str = "http://control-plane:8000/api/v1"

    # Worker (executes test jobs; must be set for Trigger Run to run tests)
    WORKER_URL: str = "http://worker:8004"

    # Optional: secret for control-plane internal API
    INTERNAL_API_SECRET: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
