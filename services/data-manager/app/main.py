"""QAtron Test Data Manager main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title="QAtron Test Data Manager",
    description="Test data management service for QAtron",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
