"""Project endpoints."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import (
    AUDIT_ACTION_PROJECT_CREATED,
    AUDIT_ACTION_PROJECT_DELETED,
    AUDIT_ACTION_PROJECT_UPDATED,
    log_audit_event,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.project import Project
from app.models.suite import Suite
from app.models.environment import Environment
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new project."""
    repo = ProjectRepository(db)
    project = repo.create(project_data)

    # Create default suite and environment so runs can be created from the UI
    default_suite = Suite(
        name="default",
        layer="e2e",
        project_id=project.id,
    )
    default_env = Environment(
        name="default",
        base_url="https://example.com",
        project_id=project.id,
    )
    db.add(default_suite)
    db.add(default_env)
    db.commit()

    # Log audit event
    log_audit_event(
        AUDIT_ACTION_PROJECT_CREATED,
        user_id=current_user.id,
        resource_type="project",
        resource_id=project.id,
        details={"name": project.name, "repo_url": str(project.repo_url)},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        db=db,
    )

    return project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """List all projects."""
    repo = ProjectRepository(db)
    projects = repo.get_all(organization_id=current_user.organization_id, skip=skip, limit=limit)
    return projects


@router.post("/{project_id}/ensure-defaults")
async def ensure_project_defaults(
    project_id: int,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    """Ensure project has at least one suite and one environment (for existing projects)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    created = []
    if db.query(Suite).filter(Suite.project_id == project_id).first() is None:
        s = Suite(name="default", layer="e2e", project_id=project_id)
        db.add(s)
        created.append("suite")
    if db.query(Environment).filter(Environment.project_id == project_id).first() is None:
        e = Environment(name="default", base_url="https://example.com", project_id=project_id)
        db.add(e)
        created.append("environment")
    db.commit()
    return {"message": "Defaults ensured", "created": created}


@router.get("/{project_id}/suites")
async def list_project_suites(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """List suites for a project (for run creation)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    suites = db.query(Suite).filter(Suite.project_id == project_id).all()
    return [{"id": s.id, "name": s.name, "layer": s.layer} for s in suites]


@router.get("/{project_id}/environments")
async def list_project_environments(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """List environments for a project (for run creation)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    envs = db.query(Environment).filter(Environment.project_id == project_id).all()
    return [{"id": e.id, "name": e.name, "base_url": e.base_url} for e in envs]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """Get a project by ID."""
    repo = ProjectRepository(db)
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    # Check organization access
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: Request,
    db: Session = Depends(get_db),
):
    """Update a project."""
    repo = ProjectRepository(db)
    project = repo.update(project_id, project_data)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Log audit event
    log_audit_event(
        AUDIT_ACTION_PROJECT_UPDATED,
        user_id=current_user.id,
        resource_type="project",
        resource_id=project_id,
        details=project_data.model_dump(exclude_unset=True),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        db=db,
    )

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: Annotated[User, Depends(require_role("admin"))],
    request: Request,
    db: Session = Depends(get_db),
):
    """Delete a project."""
    repo = ProjectRepository(db)
    # Get project name before deletion for audit log
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    success = repo.delete(project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Log audit event
    log_audit_event(
        AUDIT_ACTION_PROJECT_DELETED,
        user_id=current_user.id,
        resource_type="project",
        resource_id=project_id,
        details={"name": project.name},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        db=db,
    )
