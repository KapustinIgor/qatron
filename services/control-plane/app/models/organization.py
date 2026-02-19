"""Organization model."""
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Organization(Base):
    """Organization model (single-tenant per installation)."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    service_tokens = relationship("ServiceToken", back_populates="organization")
