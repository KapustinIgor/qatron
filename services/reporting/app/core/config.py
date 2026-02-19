"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "QAtron Reporting"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    # Database
    DATABASE_URL: str = "postgresql://qatron:qatron@postgres:5432/qatron"

    # S3/MinIO
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY_ID: str = "minioadmin"
    S3_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "qatron-artifacts"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # Allure
    ALLURE_RESULTS_PATH: str = "/tmp/allure-results"
    ALLURE_REPORTS_PATH: str = "/tmp/allure-reports"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
