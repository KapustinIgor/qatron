"""Suite model."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Suite(Base):
    """Test suite model."""

    __tablename__ = "suites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    layer = Column(String(50), nullable=False)  # unit, contract, integration, e2e
    tags = Column(JSON)  # List of tags for test selection
    shards = Column(Integer, default=1)  # Number of shards for parallel execution
    retries = Column(Integer, default=0)  # Default retry count
    timeout = Column(Integer)  # Timeout in seconds
    require_dataset_health = Column(Boolean, default=False)  # Require dataset validation before run
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="suites")
    runs = relationship("Run", back_populates="suite")
