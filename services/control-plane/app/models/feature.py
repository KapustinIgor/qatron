"""Feature, Scenario, and Step models for BDD."""
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Feature(Base):
    """BDD Feature model (indexed from repos)."""

    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(String(500))  # JSON array of tags
    last_seen_commit = Column(String(40))  # Last commit where feature was seen
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="features")
    scenarios = relationship("Scenario", back_populates="feature", cascade="all, delete-orphan")


class Scenario(Base):
    """BDD Scenario model."""

    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(String(500))  # JSON array of tags
    scenario_type = Column(String(50), default="scenario")  # scenario or scenario_outline
    examples = Column(Text)  # JSON array of arrays for examples table
    line_number = Column(Integer)
    is_flaky = Column(Boolean, default=False)
    is_quarantined = Column(Boolean, default=False)
    flakiness_score = Column(Float)  # 0.0 to 1.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    feature = relationship("Feature", back_populates="scenarios")
    steps = relationship("Step", back_populates="scenario", cascade="all, delete-orphan")


class Step(Base):
    """BDD Step model."""

    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False, index=True)
    step_type = Column(String(20), nullable=False)  # Given, When, Then, And, But
    keyword = Column(String(50), nullable=False)  # The keyword (Given/When/Then/And/But)
    text = Column(Text, nullable=False)  # The step text after keyword
    order = Column(Integer, nullable=False, default=0)  # Order within scenario
    line_number = Column(Integer)
    data_table = Column(Text)  # JSON array of arrays for data tables
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    scenario = relationship("Scenario", back_populates="steps")
