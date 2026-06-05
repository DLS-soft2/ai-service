def test_valid_request_returns_200_with_rankings(client, sample_request):
    response = client.post("/api/v1/assignments/score", content=sample_request.model_dump_json())
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == str(sample_request.order_id)
    assert len(data["rankings"]) == 2


def test_rankings_sorted_by_score_descending(client, sample_request):
    data = client.post("/api/v1/assignments/score", content=sample_request.model_dump_json()).json()
    scores = [r["score"] for r in data["rankings"]]
    assert scores == sorted(scores, reverse=True)


def test_rankings_have_required_fields(client, sample_request):
    data = client.post("/api/v1/assignments/score", content=sample_request.model_dump_json()).json()
    for ranking in data["rankings"]:
        assert "courier_id" in ranking
        assert 0.0 <= ranking["score"] <= 1.0
        assert isinstance(ranking["estimated_delivery_minutes"], int)
        assert ranking["estimated_delivery_minutes"] > 0
        assert ranking["reasoning"]


def test_fallback_returns_200_when_ollama_unavailable(client, sample_request):
    """Ollama is not running in tests, so the fallback scorer is used automatically."""
    response = client.post("/api/v1/assignments/score", content=sample_request.model_dump_json())
    assert response.status_code == 200
    assert len(response.json()["rankings"]) > 0


def test_empty_couriers_returns_200_with_empty_rankings(client):
    payload = {
        "order_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "restaurant_location": {"lat": 55.6761, "lng": 12.5683},
        "delivery_location": {"lat": 55.68, "lng": 12.59},
        "order_total": 100.0,
        "items_count": 2,
        "couriers": [],
    }
    response = client.post("/api/v1/assignments/score", json=payload)
    assert response.status_code == 200
    assert response.json()["rankings"] == []
