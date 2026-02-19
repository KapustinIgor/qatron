"""Run orchestration tasks."""
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.sharding import create_shard_jobs

# Import Run model - in production, this would come from shared models
# For now, we'll use SQLAlchemy directly
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Run(Base):
    """Run model (simplified for orchestrator). Refs projects/suites/environments by id only; no FK in ORM so we don't require those tables in this app's metadata."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    project_id = Column(Integer)
    suite_id = Column(Integer)
    environment_id = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)


@celery_app.task(bind=True, max_retries=3)
def enqueue_run(self, run_id: int):
    """
    Enqueue a test run for execution.

    This task:
    1. Validates the run request
    2. Creates shard jobs if needed
    3. Enqueues worker jobs
    4. Updates run status
    """
    db: Session = SessionLocal()
    try:
        # Get run from database
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")

        # Update status to running
        run.status = "running"
        run.started_at = datetime.utcnow()
        db.commit()

        # Get suite configuration for sharding
        # TODO: Query suite from database to get shard count
        # For now, default to 1 shard
        shard_count = 1

        # Create shard jobs
        shard_jobs = create_shard_jobs(run_id, shard_count)

        # Enqueue worker jobs
        for job in shard_jobs:
            execute_worker_job.delay(job)

        # Update run status
        run.status = "queued"  # Will be updated by worker when it starts
        db.commit()

    except Exception as exc:
        db.rollback()
        try:
            r = db.query(Run).filter(Run.id == run_id).first()
            if r:
                r.status = "failed"
                db.commit()
        except Exception:
            db.rollback()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def execute_worker_job(self, job_payload: dict):
    """
    Execute a worker job: fetch run context from control-plane, then POST to worker.
    The worker clones the repo, runs pytest (with Selenium Grid if E2E), and posts results.
    """
    run_id = job_payload.get("run_id")
    if not run_id:
        raise ValueError("job_payload must contain run_id")

    control_plane_url = settings.CONTROL_PLANE_API_URL.rstrip("/")
    job_context_url = f"{control_plane_url}/internal/runs/{run_id}/job-context"
    headers = {}
    if getattr(settings, "INTERNAL_API_SECRET", None):
        headers["X-Internal-Secret"] = settings.INTERNAL_API_SECRET

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(job_context_url, headers=headers)
            resp.raise_for_status()
            context = resp.json()
    except httpx.HTTPError as e:
        raise self.retry(exc=e, countdown=30)

    worker_url = (getattr(settings, "WORKER_URL", None) or "").rstrip("/")
    if not worker_url:
        return  # Worker not configured; skip without failing

    execute_url = f"{worker_url}/execute"
    body = {
        "job": job_payload,
        "context": context,
    }
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(execute_url, json=body)
            resp.raise_for_status()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task
def monitor_run(run_id: int):
    """
    Monitor a run's progress.

    This task periodically checks run status and updates it.
    """
    db: Session = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            return

        # Check if run is still running and update status if needed
        # This would typically check worker status or job completion
        # For MVP, workers will update status directly via API

    finally:
        db.close()


@celery_app.task
def update_run_status(run_id: int, status: str, test_results: Optional[dict] = None):
    """
    Update run status from worker.

    Called by workers to update run status and test results.
    """
    db: Session = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            return

        run.status = status
        if status in ["completed", "failed"]:
            run.completed_at = datetime.utcnow()
            if run.started_at:
                run.duration_seconds = int((run.completed_at - run.started_at).total_seconds())

        if test_results:
            run.total_tests = test_results.get("total", 0)
            run.passed_tests = test_results.get("passed", 0)
            run.failed_tests = test_results.get("failed", 0)
            run.skipped_tests = test_results.get("skipped", 0)

        db.commit()

    finally:
        db.close()
