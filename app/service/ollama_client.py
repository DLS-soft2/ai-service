import json
import logging

import httpx

from app.config import settings
from app.models.assignments import AssignmentRequest, CourierRanking

logger = logging.getLogger(__name__)


class OllamaUnavailableError(Exception):
    """Raised when Ollama cannot produce a usable response."""


def _build_prompt(request: AssignmentRequest) -> str:
    couriers_text = "\n".join(
        f"- Courier {c.courier_id}: location ({c.current_location.lat}, {c.current_location.lng}), "
        f"vehicle: {c.vehicle_type}, rating: {c.rating}/5, active deliveries: {c.active_deliveries}"
        for c in request.couriers
    )
    return (
        "You are a courier assignment optimizer for a food delivery platform.\n"
        f"Restaurant location: ({request.restaurant_location.lat}, {request.restaurant_location.lng})\n"
        f"Delivery location: ({request.delivery_location.lat}, {request.delivery_location.lng})\n"
        f"Order total: ${request.order_total}, Items: {request.items_count}\n\n"
        f"Available couriers:\n{couriers_text}\n\n"
        "Rank each courier. Return a JSON object with a single key \"rankings\" containing an array. "
        "Each element must have: \"courier_id\" (string UUID), \"score\" (float 0-1, higher is better), "
        "\"estimated_delivery_minutes\" (positive integer), \"reasoning\" (max 8 words).\n"
        "Return ONLY the JSON object, no other text.\n/no_think"
    )


def _parse_rankings(raw: str, request: AssignmentRequest) -> list[CourierRanking]:
    """Parse LLM output into validated CourierRanking objects."""
    data = json.loads(raw)
    items = data.get("rankings", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("Expected a list of rankings")
    valid_ids = {str(c.courier_id) for c in request.couriers}
    rankings = []
    for item in items:
        cid = str(item["courier_id"])
        if cid not in valid_ids:
            continue
        rankings.append(CourierRanking(
            courier_id=item["courier_id"],
            score=max(0.0, min(1.0, float(item["score"]))),
            estimated_delivery_minutes=max(1, int(item["estimated_delivery_minutes"])),
            reasoning=str(item.get("reasoning", "LLM-scored")),
        ))
    if not rankings:
        raise ValueError("No valid rankings parsed from LLM output")
    return rankings


async def score_couriers_with_llm(request: AssignmentRequest) -> list[CourierRanking]:
    """Call Ollama to score couriers. Raises OllamaUnavailableError on any failure."""
    prompt = _build_prompt(request)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(settings.ollama_timeout_seconds, connect=10.0)) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False, "format": "json",
                      "think": False, "options": {"num_predict": 768, "num_ctx": 2048}},
            )
            response.raise_for_status()
            body = response.json()
            return _parse_rankings(body["response"], request)
    except (httpx.HTTPError, httpx.TimeoutException, KeyError, json.JSONDecodeError, ValueError, TypeError) as exc:
        logger.warning("Ollama scoring failed: %s: %s", type(exc).__name__, exc or repr(exc))
        raise OllamaUnavailableError(f"{type(exc).__name__}: {exc or repr(exc)}") from exc
