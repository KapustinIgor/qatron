"""Infrastructure resource models."""
from sqlalchemy import Column, DateTime, Integer, JSON, String, func

from app.core.database import Base


class InfrastructureResource(Base):
    """Infrastructure resource model (workers, grids, etc.)."""

    __tablename__ = "infrastructure_resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # worker, selenium_grid, etc.
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # ready, busy, unavailable
    resource_metadata = Column(JSON)  # Resource-specific metadata
    last_heartbeat = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
