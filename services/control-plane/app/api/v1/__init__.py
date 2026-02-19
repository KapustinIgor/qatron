"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import projects, runs, auth, service_tokens, features, internal

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(service_tokens.router, prefix="/auth/service-tokens", tags=["service-tokens"])
api_router.include_router(features.router, prefix="/features", tags=["features"])
api_router.include_router(internal.router, prefix="/internal", tags=["internal"])
