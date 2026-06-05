import json
import re
from contextlib import asynccontextmanager
from unittest.mock import patch

import httpx
import pytest

from app.models.assignments import CourierRanking
from app.service.ollama_client import OllamaUnavailableError, score_couriers_with_llm

_RealAsyncClient = httpx.AsyncClient


def _make_mock_client(handler):
    """Create a patched AsyncClient constructor that uses a MockTransport."""
    transport = httpx.MockTransport(handler)

    @asynccontextmanager
    async def fake_client(**_kwargs):
        async with _RealAsyncClient(transport=transport) as client:
            yield client

    return fake_client


def _ollama_success_handler(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    ids = re.findall(r"Courier ([0-9a-f-]{36})", body["prompt"])
    rankings = [
        {"courier_id": cid, "score": round(0.9 - i * 0.1, 2),
         "estimated_delivery_minutes": 15 + i * 5, "reasoning": f"Courier {i+1} analysis"}
        for i, cid in enumerate(ids)
    ]
    return httpx.Response(200, json={"response": json.dumps({"rankings": rankings})})


@pytest.mark.asyncio
async def test_successful_ollama_response_parsed(sample_request):
    with patch("app.service.ollama_client.httpx.AsyncClient", _make_mock_client(_ollama_success_handler)):
        rankings = await score_couriers_with_llm(sample_request)

    assert len(rankings) == 2
    assert all(isinstance(r, CourierRanking) for r in rankings)
    assert all(0.0 <= r.score <= 1.0 for r in rankings)
    assert all(r.estimated_delivery_minutes > 0 for r in rankings)
    assert all(r.reasoning for r in rankings)


@pytest.mark.asyncio
async def test_connection_error_raises_unavailable(sample_request):
    def raise_connection_error(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    with patch("app.service.ollama_client.httpx.AsyncClient", _make_mock_client(raise_connection_error)):
        with pytest.raises(OllamaUnavailableError):
            await score_couriers_with_llm(sample_request)


@pytest.mark.asyncio
async def test_malformed_json_raises_unavailable(sample_request):
    def return_garbage(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "not valid json {{{}"})

    with patch("app.service.ollama_client.httpx.AsyncClient", _make_mock_client(return_garbage)):
        with pytest.raises(OllamaUnavailableError):
            await score_couriers_with_llm(sample_request)


@pytest.mark.asyncio
async def test_timeout_raises_unavailable(sample_request):
    def raise_timeout(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Timed out")

    with patch("app.service.ollama_client.httpx.AsyncClient", _make_mock_client(raise_timeout)):
        with pytest.raises(OllamaUnavailableError):
            await score_couriers_with_llm(sample_request)
