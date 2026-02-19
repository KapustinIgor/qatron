"""Audit log model."""
from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, func

from app.core.database import Base


class AuditLog(Base):
    """Audit log for tracking important actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # run_triggered, config_changed, etc.
    user_id = Column(Integer)  # Nullable for system actions
    resource_type = Column(String(50))  # project, suite, dataset, etc.
    resource_id = Column(Integer)
    details = Column(JSON)  # Additional action details
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
