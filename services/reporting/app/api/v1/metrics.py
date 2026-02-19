"""Metrics endpoints."""
from typing import Optional

from fastapi import APIRouter, Query

from app.services.metrics import MetricsService

router = APIRouter()


@router.get("/runs")
async def get_run_metrics(
    project_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    """Get aggregated run metrics."""
    service = MetricsService()
    return service.get_run_metrics(project_id=project_id, days=days)


@router.get("/flakiness")
async def get_flakiness_scores(scenario_id: Optional[int] = None):
    """Get flakiness scores."""
    service = MetricsService()
    return service.get_flakiness_scores(scenario_id=scenario_id)


@router.get("/coverage/{run_id}")
async def get_coverage_metrics(run_id: int):
    """Get coverage metrics for a run."""
    service = MetricsService()
    return service.get_coverage_metrics(run_id)
