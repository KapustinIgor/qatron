"""Celery tasks for cleanup operations."""
from datetime import datetime, timedelta
from typing import Optional

from app.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.run import Run, RunArtifact


@celery_app.task(name="cleanup_artifacts")
def cleanup_artifacts(retention_days: Optional[int] = None) -> dict:
    """Clean up old artifacts based on retention policy."""
    if retention_days is None:
        retention_days = settings.CELERY_ARTIFACT_RETENTION_DAYS
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Find runs older than retention period
        old_runs = db.query(Run).filter(
            Run.completed_at.isnot(None),
            Run.completed_at < cutoff_date,
            Run.status.in_(["completed", "failed", "cancelled", "partial_failed", "timed_out", "infra_failed"]),
        ).all()

        deleted_artifacts = 0

        for run in old_runs:
            artifacts = db.query(RunArtifact).filter(RunArtifact.run_id == run.id).all()
            for artifact in artifacts:
                # TODO: Delete from S3/MinIO when integrated
                # from app.core.s3 import get_client; get_client().delete_object(Bucket=artifact.s3_bucket, Key=artifact.s3_key)
                db.delete(artifact)
                deleted_artifacts += 1

        db.commit()

        return {
            "deleted_artifacts": deleted_artifacts,
            "cutoff_date": cutoff_date.isoformat(),
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="cleanup_expired_tokens")
def cleanup_expired_tokens() -> dict:
    """Deactivate expired service tokens."""
    from app.models.service_token import ServiceToken

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        expired_tokens = db.query(ServiceToken).filter(
            ServiceToken.expires_at.isnot(None),
            ServiceToken.expires_at < now,
            ServiceToken.is_active.is_(True),
        ).all()

        for token in expired_tokens:
            token.is_active = False

        db.commit()

        return {"deactivated_tokens": len(expired_tokens)}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
