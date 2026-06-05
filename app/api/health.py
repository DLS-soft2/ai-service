import httpx
from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Liveness probe with Ollama connectivity status."""
    ollama_status = await _check_ollama()
    status = "healthy" if ollama_status == "connected" else "degraded"
    return {"status": status, "ollama": ollama_status}


async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            return "connected"
    except (httpx.HTTPError, httpx.TimeoutException):
        return "unavailable"
