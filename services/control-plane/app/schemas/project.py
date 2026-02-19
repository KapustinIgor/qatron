"""Project schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str
    description: Optional[str] = None
    repo_url: HttpUrl
    repo_auth_method: str  # 'token' or 'ssh'


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    organization_id: int
    repo_auth_secret_ref: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Project update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    repo_url: Optional[HttpUrl] = None
    repo_auth_method: Optional[str] = None
    repo_auth_secret_ref: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: int
    organization_id: int
    repo_auth_secret_ref: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
