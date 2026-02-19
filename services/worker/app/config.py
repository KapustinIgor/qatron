"""Worker configuration."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Worker configuration."""

    s3_endpoint_url: str
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_bucket_name: str
    s3_region: str = "us-east-1"


def get_config() -> Config:
    """Get worker configuration from environment."""
    return Config(
        s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://minio:9000"),
        s3_access_key_id=os.getenv("S3_ACCESS_KEY_ID", "minioadmin"),
        s3_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin"),
        s3_bucket_name=os.getenv("S3_BUCKET_NAME", "qatron-artifacts"),
        s3_region=os.getenv("S3_REGION", "us-east-1"),
    )
