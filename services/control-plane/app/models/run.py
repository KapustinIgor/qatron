"""Run model."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Run(Base):
    """Test run model."""

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(
        String(50), nullable=False, index=True
    )  # queued, provisioning, running, reporting, completed, failed, partial_failed, timed_out, infra_failed, cancelled
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    suite_id = Column(Integer, ForeignKey("suites.id"), nullable=False)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=False)
    branch = Column(String(255), index=True)
    commit = Column(String(40), index=True)  # Git commit SHA
    commit_message = Column(Text)
    triggered_by = Column(String(255))  # User or CI system
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    dataset_version = Column(String(100))  # Dataset version/hash used
    run_metadata = Column(JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="runs")
    suite = relationship("Suite", back_populates="runs")
    environment = relationship("Environment", back_populates="runs")
    artifacts = relationship("RunArtifact", back_populates="run", cascade="all, delete-orphan")


class RunArtifact(Base):
    """Run artifact model (references to S3 objects)."""

    __tablename__ = "run_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False)  # allure, screenshot, log, coverage, video
    s3_key = Column(String(500), nullable=False)  # S3 object key
    s3_bucket = Column(String(255), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    run = relationship("Run", back_populates="artifacts")
