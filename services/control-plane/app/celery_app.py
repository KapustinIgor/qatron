"""Celery application for control-plane background tasks."""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "qatron_control_plane",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.cleanup"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)

# Celery Beat schedule for periodic cleanup
celery_app.conf.beat_schedule = {
    "cleanup-artifacts-daily": {
        "task": "cleanup_artifacts",
        "schedule": crontab(hour=3, minute=0),  # 03:00 UTC daily
        "kwargs": {"retention_days": settings.CELERY_ARTIFACT_RETENTION_DAYS},
    },
    "cleanup-expired-tokens-daily": {
        "task": "cleanup_expired_tokens",
        "schedule": crontab(hour=4, minute=0),  # 04:00 UTC daily
    },
}
