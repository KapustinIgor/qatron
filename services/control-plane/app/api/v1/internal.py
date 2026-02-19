"""Internal API for orchestrator/worker (no user auth)."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.environment import Environment
from app.models.project import Project
from app.models.run import Run
from app.models.suite import Suite

router = APIRouter()


def verify_internal(
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret"),
) -> None:
    """Allow request if INTERNAL_API_SECRET is not set or header matches."""
    secret = getattr(settings, "INTERNAL_API_SECRET", None)
    if not secret:
        return
    if x_internal_secret != secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Internal-Secret",
        )


@router.get(
    "/runs/{run_id}/job-context",
    response_model=dict,
    dependencies=[],
)
async def get_run_job_context(
    run_id: int,
    _: None = Depends(verify_internal),
    db: Session = Depends(get_db),
):
    """
    Return job context for a run (repo_url, suite name, environment name, etc.).
    Used by the orchestrator to pass context to the worker. Internal only.
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    project = db.query(Project).filter(Project.id == run.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    suite = db.query(Suite).filter(Suite.id == run.suite_id).first()
    environment = db.query(Environment).filter(Environment.id == run.environment_id).first()
    # Use defaults if suite/environment missing (e.g. run created before ensure-defaults)
    suite_name = suite.name if suite else "default"
    layer = (suite.layer if suite else None) or "e2e"
    environment_name = (environment.name if environment else None) or "default"

    return {
        "run_id": run.id,
        "project_id": run.project_id,
        "repo_url": str(project.repo_url),
        "branch": run.branch or "HEAD",
        "commit": run.commit or "HEAD",
        "suite_id": run.suite_id,
        "suite_name": suite_name,
        "layer": layer,
        "environment_id": run.environment_id,
        "environment_name": environment_name,
    }


@router.put("/runs/{run_id}/results")
async def update_run_results(
    run_id: int,
    body: dict,
    _: None = Depends(verify_internal),
    db: Session = Depends(get_db),
):
    """
    Update run with test results (status, counts). Used by the worker. Internal only.
    """
    from datetime import datetime

    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    run.status = body.get("status", run.status)
    if run.status == "running" and not run.started_at:
        run.started_at = datetime.utcnow()
    if "total_tests" in body:
        run.total_tests = body["total_tests"]
    if "passed_tests" in body:
        run.passed_tests = body["passed_tests"]
    if "failed_tests" in body:
        run.failed_tests = body["failed_tests"]
    if "skipped_tests" in body:
        run.skipped_tests = body["skipped_tests"]
    if run.status in ("completed", "failed"):
        run.completed_at = datetime.utcnow()
        if run.started_at:
            run.duration_seconds = int((run.completed_at - run.started_at).total_seconds())
    db.commit()
    db.refresh(run)
    return {"ok": True}
