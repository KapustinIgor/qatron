"""QAtron Control Plane API main application."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and default data on startup with retries."""
    Base.metadata.create_all(bind=engine)
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            init_db()
            break
        except Exception as e:
            if attempt < max_attempts - 1:
                wait = 2 ** attempt
                print(f"Init DB attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"Warning: Could not initialize default data after {max_attempts} attempts: {e}")
    yield


app = FastAPI(
    title="QAtron Control Plane API",
    description="Control Plane API for QAtron QA automation platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
    # TODO: Check database connectivity
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
