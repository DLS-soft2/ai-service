from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.assignments import router as assignments_router
from app.api.health import router as health_router
from app.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup and shutdown lifecycle hooks."""
    yield


app = FastAPI(
    title="AI Service",
    description="AI service for the DLS-2 food delivery platform",
    version=settings.service_version,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(assignments_router)


@app.get("/")
def root():
    """Service info endpoint."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
    }
