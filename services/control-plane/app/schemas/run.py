"""Run schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RunBase(BaseModel):
    """Base run schema."""

    project_id: int
    suite_id: int
    environment_id: int
    branch: Optional[str] = None
    commit: Optional[str] = None
    commit_message: Optional[str] = None
    triggered_by: Optional[str] = None


class RunCreate(RunBase):
    """Run creation schema."""

    pass


class RunUpdate(BaseModel):
    """Run update schema."""

    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_tests: Optional[int] = None
    passed_tests: Optional[int] = None
    failed_tests: Optional[int] = None
    skipped_tests: Optional[int] = None
    dataset_version: Optional[str] = None
    run_metadata: Optional[dict] = None  # For shard tracking, coverage, etc.


class RunResponse(RunBase):
    """Run response schema."""

    id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    dataset_version: Optional[str] = None
    run_metadata: Optional[dict] = None  # Shard tracking, coverage, etc.
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
