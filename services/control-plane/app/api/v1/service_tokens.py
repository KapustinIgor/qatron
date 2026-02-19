"""Service token endpoints for CI/CD integration."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.audit import AUDIT_ACTION_SERVICE_TOKEN_CREATED, AUDIT_ACTION_SERVICE_TOKEN_REVOKED, log_audit_event
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.security import generate_service_token, hash_service_token
from app.models.service_token import ServiceToken
from app.models.user import User
from app.schemas.service_token import ServiceTokenCreate, ServiceTokenCreateResponse, ServiceTokenResponse

router = APIRouter()


@router.post("", response_model=ServiceTokenCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_service_token(
    token_data: ServiceTokenCreate,
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new service token for CI/CD integration."""
    # Verify organization access
    if token_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create token for different organization",
        )

    # Verify project access if scoped
    if token_data.project_id:
        from app.models.project import Project
        project = db.query(Project).filter(Project.id == token_data.project_id).first()
        if not project or project.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied",
            )

    # Generate token (only shown once)
    token = generate_service_token()
    token_hash = hash_service_token(token)

    # Create service token record
    service_token = ServiceToken(
        name=token_data.name,
        description=token_data.description,
        token_hash=token_hash,
        organization_id=token_data.organization_id,
        project_id=token_data.project_id,
        created_by_user_id=current_user.id,
        expires_at=token_data.expires_at,
        is_active=True,
    )
    db.add(service_token)
    db.commit()
    db.refresh(service_token)

    # Log audit event
    log_audit_event(
        AUDIT_ACTION_SERVICE_TOKEN_CREATED,
        user_id=current_user.id,
        resource_type="service_token",
        resource_id=service_token.id,
        details={"name": token_data.name, "project_id": token_data.project_id},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        db=db,
    )

    return ServiceTokenCreateResponse(
        token=token,  # Only time token is returned
        service_token=ServiceTokenResponse.model_validate(service_token),
    )


@router.get("", response_model=List[ServiceTokenResponse])
async def list_service_tokens(
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    """List service tokens for current organization."""
    tokens = (
        db.query(ServiceToken)
        .filter(ServiceToken.organization_id == current_user.organization_id)
        .order_by(ServiceToken.created_at.desc())
        .all()
    )
    return tokens


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_service_token(
    token_id: int,
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: Request,
    db: Session = Depends(get_db),
):
    """Revoke a service token."""
    token = (
        db.query(ServiceToken)
        .filter(
            ServiceToken.id == token_id,
            ServiceToken.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service token not found")

    token.is_active = False
    db.commit()

    # Log audit event
    log_audit_event(
        AUDIT_ACTION_SERVICE_TOKEN_REVOKED,
        user_id=current_user.id,
        resource_type="service_token",
        resource_id=token_id,
        details={"name": token.name},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        db=db,
    )
