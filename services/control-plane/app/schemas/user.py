"""User schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str
    organization_id: int


class UserResponse(UserBase):
    """User response schema."""

    id: int
    is_active: bool
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
