"""Service token model for CI/CD integration."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ServiceToken(Base):
    """Service token for programmatic API access (CI/CD)."""

    __tablename__ = "service_tokens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Human-readable name
    token_hash = Column(String(255), nullable=False, unique=True, index=True)  # Hashed token
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # Optional project scope
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Null = no expiry
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text)  # Optional description
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="service_tokens")
    project = relationship("Project")
    created_by = relationship("User")
