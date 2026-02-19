"""Run endpoints."""
from typing import Annotated, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import AUDIT_ACTION_RUN_TRIGGERED, log_audit_event
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.run import RunRepository
from app.schemas.run import RunCreate, RunResponse, RunUpdate

router = APIRouter()


@router.post("", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    run_data: RunCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    request: Request,
    db: Session = Depends(get_db),
):
    """Create and trigger a new test run."""
    # Validate dataset if required (gating)
    from app.models.environment import Environment
    from app.models.suite import Suite
    from app.services.dataset_validator import DatasetValidator

    suite = db.query(Suite).filter(Suite.id == run_data.suite_id).first()
    if suite and suite.require_dataset_health:
        environment = db.query(Environment).filter(Environment.id == run_data.environment_id).first()
        if environment and environment.dataset_id:
            # Get latest dataset version
            from app.models.dataset import DatasetVersion
            dataset_version = (
                db.query(DatasetVersion)
                .filter(DatasetVersion.dataset_id == environment.dataset_id)
                .order_by(DatasetVersion.created_at.desc())
                .first()
            )
            if dataset_version:
                # Validate dataset before run
                is_valid, error_msg = DatasetValidator.validate_before_run(
                    dataset_version.id,
                    db,
                    fail_fast=True,
                )
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Dataset validation failed: {error_msg}",
                    )

    repo = RunRepository(db)
    run = repo.create(run_data)
    # TODO: Trigger orchestrator to enqueue the run

    # Log audit event
    log_audit_event(
        AUDIT_ACTION_RUN_TRIGGERED,
        user_id=current_user.id,
        resource_type="run",
        resource_id=run.id,
        details={
            "project_id": run.project_id,
            "suite_id": run.suite_id,
            "environment_id": run.environment_id,
            "branch": run.branch,
            "commit": run.commit,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        db=db,
    )

    return run


@router.get("", response_model=List[RunResponse])
async def list_runs(
    project_id: Optional[int] = None,
    suite_id: Optional[int] = None,
    environment_id: Optional[int] = None,
    status: Optional[str] = None,
    branch: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """List all runs with optional filtering."""
    repo = RunRepository(db)
    runs = repo.get_all(
        project_id=project_id,
        suite_id=suite_id,
        environment_id=environment_id,
        status=status,
        branch=branch,
        skip=skip,
        limit=limit,
    )
    return runs


@router.post("/{run_id}/trigger")
async def trigger_run(
    run_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Trigger a queued run: send it to the orchestrator for execution."""
    repo = RunRepository(db)
    run = repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.status != "queued":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Run is not queued (current status: {run.status}). Only queued runs can be triggered.",
        )
    orchestrator_url = settings.ORCHESTRATOR_URL.rstrip("/")
    enqueue_url = f"{orchestrator_url}/api/v1/runs/{run_id}/enqueue"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(enqueue_url)
            resp.raise_for_status()
    except httpx.ConnectError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Orchestrator is not reachable. Start it with: "
                "docker compose up -d orchestrator orchestrator-worker"
            ),
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Orchestrator error: {str(e)}",
        )
    return {"message": "Run triggered", "run_id": run_id}


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """Get a run by ID."""
    repo = RunRepository(db)
    run = repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.put("/{run_id}", response_model=RunResponse)
async def update_run(
    run_id: int,
    run_data: RunUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Update a run."""
    repo = RunRepository(db)
    run = repo.update(run_id, run_data)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run
