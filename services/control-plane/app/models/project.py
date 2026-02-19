"""Project model."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    repo_url = Column(String(500), nullable=False)
    repo_auth_method = Column(String(50), nullable=False)  # 'token' or 'ssh'
    repo_auth_secret_ref = Column(String(255))  # Reference to K8s secret
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    environments = relationship("Environment", back_populates="project", cascade="all, delete-orphan")
    suites = relationship("Suite", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="project", cascade="all, delete-orphan")
    features = relationship("Feature", back_populates="project", cascade="all, delete-orphan")
