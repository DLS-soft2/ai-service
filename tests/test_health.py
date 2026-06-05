def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_reports_ollama_unavailable_when_not_running(client):
    data = client.get("/health").json()
    assert data["ollama"] == "unavailable"
    assert data["status"] == "degraded"


def test_root_returns_200_with_service_name(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ai-service"
