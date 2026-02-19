"""Dataset models."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dataset(Base):
    """Dataset model."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    dataset_type = Column(String(50))  # database, api, file, etc.
    refresh_mechanism = Column(String(50))  # manual, scheduled, webhook
    validation_rules_ref = Column(String(500))  # Reference to validation rules
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    environments = relationship("Environment", back_populates="dataset")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(Base):
    """Dataset version model."""

    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    version = Column(String(100), nullable=False)  # Version or hash
    storage_path = Column(String(500))  # Path to dataset file (S3 or local)
    health_status = Column(String(50))  # healthy, unhealthy, unknown
    validation_status = Column(String(50))  # passed, failed, pending
    validation_report_ref = Column(String(500))  # S3 reference to validation report
    expectations = Column(Text)  # JSON expectation suite for Great Expectations
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="versions")
