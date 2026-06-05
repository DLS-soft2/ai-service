import logging

from app.models.assignments import AssignmentRequest, AssignmentResponse
from app.service.fallback_scorer import score_couriers_by_distance
from app.service.ollama_client import OllamaUnavailableError, score_couriers_with_llm

logger = logging.getLogger(__name__)


async def score_assignment(request: AssignmentRequest) -> AssignmentResponse:
    """Score couriers via LLM, falling back to deterministic distance-based scoring."""
    try:
        rankings = await score_couriers_with_llm(request)
    except OllamaUnavailableError:
        logger.warning("Ollama unavailable, using fallback scorer for order %s", request.order_id)
        rankings = score_couriers_by_distance(request)

    rankings.sort(key=lambda r: r.score, reverse=True)
    return AssignmentResponse(order_id=request.order_id, rankings=rankings)
