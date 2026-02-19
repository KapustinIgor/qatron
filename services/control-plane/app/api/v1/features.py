"""BDD feature ingestion endpoints."""
import json
from pathlib import Path
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.feature import Feature, Scenario, Step
from app.models.project import Project
from app.services.bdd_parser import GherkinParser

router = APIRouter()


class IngestFeaturesBody(BaseModel):
    """Request body for feature ingestion."""
    repo_path: str


class FeatureContentItem(BaseModel):
    """One feature file content for ingestion."""
    file_path: str
    content: str


class IngestFromContentBody(BaseModel):
    """Request body for ingesting from raw Gherkin content."""
    features: List[FeatureContentItem]


def _store_parsed_features(db: Session, project_id: int, parsed_features: List[dict]) -> int:
    """Store parsed feature data into DB. Returns count of features stored."""
    ingested_count = 0
    for feature_data in parsed_features:
        feature = (
            db.query(Feature)
            .filter(Feature.project_id == project_id, Feature.file_path == feature_data["file_path"])
            .first()
        )
        if not feature:
            feature = Feature(
                project_id=project_id,
                name=feature_data["name"],
                file_path=feature_data["file_path"],
                description=feature_data.get("description"),
                tags=json.dumps(feature_data.get("tags", [])),
            )
            db.add(feature)
            db.flush()
        else:
            feature.name = feature_data["name"]
            feature.description = feature_data.get("description")
            feature.tags = json.dumps(feature_data.get("tags", []))
            db.query(Scenario).filter(Scenario.feature_id == feature.id).delete()

        for scenario_data in feature_data.get("scenarios", []):
            scenario = Scenario(
                feature_id=feature.id,
                name=scenario_data["name"],
                scenario_type=scenario_data.get("type", "scenario"),
                tags=json.dumps(scenario_data.get("tags", [])),
                examples=json.dumps(scenario_data.get("examples", [])) if scenario_data.get("examples") else None,
            )
            db.add(scenario)
            db.flush()
            for order, step_data in enumerate(scenario_data.get("steps", []), start=1):
                step_text = step_data["text"]
                keyword = step_data["type"].capitalize()
                if step_text.lower().startswith(keyword.lower()):
                    text = step_text[len(keyword) :].strip()
                else:
                    text = step_text
                step = Step(
                    scenario_id=scenario.id,
                    step_type=step_data["type"],
                    keyword=keyword,
                    text=text,
                    order=order,
                    data_table=json.dumps(step_data.get("data_table")) if step_data.get("data_table") else None,
                )
                db.add(step)
        ingested_count += 1
    return ingested_count


@router.post("/projects/{project_id}/ingest-features", status_code=status.HTTP_200_OK)
async def ingest_features(
    project_id: int,
    body: IngestFeaturesBody,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    """Ingest BDD features from a repository."""
    repo_path = body.repo_path
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Parse features
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Repository path does not exist")

    parsed_features = GherkinParser.scan_repository(repo_path_obj)
    ingested_count = _store_parsed_features(db, project_id, parsed_features)
    db.commit()
    return {"message": f"Successfully ingested {ingested_count} features", "features_count": ingested_count}


@router.post("/projects/{project_id}/ingest-features-from-content", status_code=status.HTTP_200_OK)
async def ingest_features_from_content(
    project_id: int,
    body: IngestFromContentBody,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    """Ingest BDD features from raw Gherkin content (e.g. paste from UI)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    parsed_features = []
    for item in body.features:
        parsed = GherkinParser.parse_feature_content(item.content, item.file_path)
        if parsed:
            parsed_features.append(parsed)
    if not parsed_features:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid feature content could be parsed",
        )

    ingested_count = _store_parsed_features(db, project_id, parsed_features)
    db.commit()
    return {"message": f"Successfully ingested {ingested_count} features", "features_count": ingested_count}


@router.get("/projects/{project_id}/features", response_model=List[dict])
async def list_features(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """List BDD features for a project."""
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    features = db.query(Feature).filter(Feature.project_id == project_id).all()
    result = []
    for feature in features:
        scenarios = db.query(Scenario).filter(Scenario.feature_id == feature.id).all()
        scenario_list = []
        for scenario in scenarios:
            steps = db.query(Step).filter(Step.scenario_id == scenario.id).order_by(Step.order).all()
            scenario_list.append({
                "id": scenario.id,
                "name": scenario.name,
                "type": scenario.scenario_type,
                "tags": json.loads(scenario.tags) if scenario.tags else [],
                "steps": [{"type": s.step_type, "keyword": s.keyword, "text": s.text} for s in steps],
            })
        result.append({
            "id": feature.id,
            "name": feature.name,
            "file_path": feature.file_path,
            "description": feature.description,
            "tags": json.loads(feature.tags) if feature.tags else [],
            "scenarios": scenario_list,
        })
    return result
