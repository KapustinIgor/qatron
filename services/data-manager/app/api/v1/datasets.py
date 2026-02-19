"""Dataset management endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.services.validation import ValidationService

router = APIRouter()


@router.get("")
async def list_datasets() -> List[dict]:
    """List all datasets."""
    # TODO: Query from database
    return []


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: int) -> dict:
    """Get dataset details."""
    # TODO: Query from database
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")


@router.post("/{dataset_id}/validate")
async def validate_dataset(dataset_id: int) -> dict:
    """Trigger dataset validation."""
    service = ValidationService()
    return service.validate_dataset(dataset_id)


@router.get("/{dataset_id}/health")
async def get_dataset_health(dataset_id: int) -> dict:
    """Get dataset health status."""
    service = ValidationService()
    health_status = service.get_health_status(dataset_id)
    return {"dataset_id": dataset_id, "health_status": health_status}
