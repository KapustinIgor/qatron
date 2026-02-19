"""Audit logging utilities."""
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.audit_log import AuditLog


def log_audit_event(
    action: str,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Optional[Session] = None,
) -> None:
    """Log an audit event."""
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False

    try:
        audit_log = AuditLog(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        db.rollback()
        # Don't fail the main operation if audit logging fails
        print(f"Warning: Failed to log audit event: {e}")
    finally:
        if should_close:
            db.close()


# Common audit actions
AUDIT_ACTION_LOGIN = "user.login"
AUDIT_ACTION_LOGOUT = "user.logout"
AUDIT_ACTION_RUN_TRIGGERED = "run.triggered"
AUDIT_ACTION_PROJECT_CREATED = "project.created"
AUDIT_ACTION_PROJECT_UPDATED = "project.updated"
AUDIT_ACTION_PROJECT_DELETED = "project.deleted"
AUDIT_ACTION_SECRET_UPDATED = "secret.updated"
AUDIT_ACTION_ROLE_ASSIGNED = "role.assigned"
AUDIT_ACTION_ROLE_REMOVED = "role.removed"
AUDIT_ACTION_SERVICE_TOKEN_CREATED = "service_token.created"
AUDIT_ACTION_SERVICE_TOKEN_REVOKED = "service_token.revoked"
