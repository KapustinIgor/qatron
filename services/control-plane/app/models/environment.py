"""Environment model."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Environment(Base):
    """Environment model."""

    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(500))
    api_url = Column(String(500))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="environments")
    dataset = relationship("Dataset", back_populates="environments")
    runs = relationship("Run", back_populates="environment")
