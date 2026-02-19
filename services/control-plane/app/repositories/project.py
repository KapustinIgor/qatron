"""Project repository."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Repository for project operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        # Convert Pydantic model to dict, converting HttpUrl to string
        data = project_data.model_dump(mode='json')
        project = Project(**data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_all(self, organization_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with optional filtering."""
        query = self.db.query(Project)
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        return query.offset(skip).limit(limit).all()

    def update(self, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        """Update a project."""
        project = self.get_by_id(project_id)
        if not project:
            return None
        # Convert Pydantic model to dict, converting HttpUrl to string
        update_data = project_data.model_dump(exclude_unset=True, mode='json')
        for field, value in update_data.items():
            setattr(project, field, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        """Delete a project."""
        project = self.get_by_id(project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True
