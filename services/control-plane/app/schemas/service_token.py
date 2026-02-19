"""Service token schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ServiceTokenCreate(BaseModel):
    """Service token creation schema."""

    name: str
    description: Optional[str] = None
    organization_id: int
    project_id: Optional[int] = None  # Optional project scope
    expires_at: Optional[datetime] = None  # None = no expiry


class ServiceTokenResponse(BaseModel):
    """Service token response schema."""

    id: int
    name: str
    description: Optional[str] = None
    organization_id: int
    project_id: Optional[int] = None
    created_by_user_id: int
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceTokenCreateResponse(BaseModel):
    """Response when creating a service token (includes the token itself)."""

    token: str  # Only returned once on creation
    service_token: ServiceTokenResponse
