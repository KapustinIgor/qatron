"""FastAPI dependencies."""
from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token, hash_service_token, verify_password
from app.models.service_token import ServiceToken
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user (JWT or service token)."""
    token = credentials.credentials

    # Try JWT first (user login)
    payload = decode_access_token(token)
    if payload:
        sub = payload.get("sub")
        if sub:
            try:
                user_id = int(sub)
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.is_active:
                    return user
            except (TypeError, ValueError):
                pass

    # Try service token
    # Service tokens are stored hashed, so we need to check all active tokens
    # In production, use a more efficient lookup (e.g., token prefix index)
    service_tokens = db.query(ServiceToken).filter(ServiceToken.is_active == True).all()
    for st in service_tokens:
        try:
            if verify_password(token, st.token_hash):
                # Check expiry
                if st.expires_at and st.expires_at < datetime.utcnow():
                    continue
                # Update last_used_at
                st.last_used_at = datetime.utcnow()
                db.commit()
                # Return a system user or create a proxy user
                # For now, return the creator user
                user = db.query(User).filter(User.id == st.created_by_user_id).first()
                if user and user.is_active:
                    return user
        except Exception:
            continue

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(role_name: str):
    """Dependency factory for requiring a specific role."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_names = [role.name for role in current_user.roles]
        if role_name not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {role_name} role",
            )
        return current_user

    return role_checker
