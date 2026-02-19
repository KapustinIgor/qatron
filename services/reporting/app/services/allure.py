"""Allure report generation service."""
import os
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

import boto3

from app.core.config import settings


class AllureService:
    """Service for generating Allure reports."""

    def __init__(self):
        """Initialize Allure service."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )

    def download_results(self, run_id: int, shard_index: Optional[int] = None) -> Path:
        """Download Allure results from S3."""
        results_dir = Path(settings.ALLURE_RESULTS_PATH) / f"run-{run_id}"
        if shard_index is not None:
            results_dir = results_dir / f"shard-{shard_index}"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Download from S3
        s3_prefix = f"runs/{run_id}"
        if shard_index is not None:
            s3_prefix = f"{s3_prefix}/shard-{shard_index}"

        s3_prefix = f"{s3_prefix}/allure/"

        # List and download files
        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=settings.S3_BUCKET_NAME, Prefix=s3_prefix):
            if "Contents" in page:
                for obj in page["Contents"]:
                    key = obj["Key"]
                    if key.endswith(".zip"):
                        # Download and extract zip
                        local_zip = results_dir / Path(key).name
                        self.s3_client.download_file(
                            settings.S3_BUCKET_NAME, key, str(local_zip)
                        )
                        with zipfile.ZipFile(local_zip, "r") as zip_ref:
                            zip_ref.extractall(results_dir)
                        local_zip.unlink()

        return results_dir

    def generate_report(self, results_dir: Path, report_id: str) -> Path:
        """Generate Allure report from results."""
        report_dir = Path(settings.ALLURE_REPORTS_PATH) / report_id
        report_dir.mkdir(parents=True, exist_ok=True)

        # Run Allure generate
        subprocess.run(
            [
                "allure",
                "generate",
                str(results_dir),
                "-o",
                str(report_dir),
                "--clean",
            ],
            check=True,
        )

        return report_dir

    def upload_report(self, report_dir: Path, run_id: int):
        """Upload Allure report to S3."""
        s3_prefix = f"reports/{run_id}/allure/"

        for file_path in report_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(report_dir)
                s3_key = f"{s3_prefix}{relative_path}"
                self.s3_client.upload_file(
                    str(file_path), settings.S3_BUCKET_NAME, s3_key
                )

    def get_report_url(self, run_id: int) -> str:
        """Get URL to view Allure report."""
        return f"/api/v1/reports/{run_id}/allure"
