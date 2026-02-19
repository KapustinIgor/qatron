"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import reports, metrics

api_router = APIRouter()

api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
