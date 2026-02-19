"""Run repository."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.run import Run
from app.schemas.run import RunCreate, RunUpdate


class RunRepository:
    """Repository for run operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, run_data: RunCreate) -> Run:
        """Create a new run."""
        run = Run(status="queued", **run_data.model_dump())
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_by_id(self, run_id: int) -> Optional[Run]:
        """Get run by ID."""
        return self.db.query(Run).filter(Run.id == run_id).first()

    def get_all(
        self,
        project_id: Optional[int] = None,
        suite_id: Optional[int] = None,
        environment_id: Optional[int] = None,
        status: Optional[str] = None,
        branch: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Run]:
        """Get all runs with optional filtering."""
        query = self.db.query(Run)
        if project_id:
            query = query.filter(Run.project_id == project_id)
        if suite_id:
            query = query.filter(Run.suite_id == suite_id)
        if environment_id:
            query = query.filter(Run.environment_id == environment_id)
        if status:
            query = query.filter(Run.status == status)
        if branch:
            query = query.filter(Run.branch == branch)
        return query.order_by(Run.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, run_id: int, run_data: RunUpdate) -> Optional[Run]:
        """Update a run."""
        run = self.get_by_id(run_id)
        if not run:
            return None
        update_data = run_data.model_dump(exclude_unset=True)
        # Handle run_metadata separately (merge with existing)
        if "run_metadata" in update_data:
            existing_metadata = run.run_metadata or {}
            existing_metadata.update(update_data.pop("run_metadata"))
            run.run_metadata = existing_metadata
        for field, value in update_data.items():
            setattr(run, field, value)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_shard_results(self, run_id: int, shard_id: int, shard_result: dict) -> Optional[Run]:
        """Update shard results in run_metadata."""
        run = self.get_by_id(run_id)
        if not run:
            return None
        if not run.run_metadata:
            run.run_metadata = {}
        if "shards" not in run.run_metadata:
            run.run_metadata["shards"] = {}
        run.run_metadata["shards"][str(shard_id)] = shard_result
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_coverage(self, run_id: int, coverage_data: dict) -> Optional[Run]:
        """Update coverage data in run_metadata."""
        run = self.get_by_id(run_id)
        if not run:
            return None
        if not run.run_metadata:
            run.run_metadata = {}
        run.run_metadata["coverage"] = coverage_data
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_status(self, run_id: int, status: str, started_at: Optional[datetime] = None, completed_at: Optional[datetime] = None) -> Optional[Run]:
        """Update run status and timestamps."""
        run = self.get_by_id(run_id)
        if not run:
            return None
        run.status = status
        if started_at:
            run.started_at = started_at
        if completed_at:
            run.completed_at = completed_at
            if run.started_at:
                run.duration_seconds = int((completed_at - run.started_at).total_seconds())
        self.db.commit()
        self.db.refresh(run)
        return run
