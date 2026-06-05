import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.assignments import AssignmentRequest, CourierCandidate, Location


@pytest.fixture(name="client")
def fixture_client():
    """HTTP test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="sample_request")
def fixture_sample_request() -> AssignmentRequest:
    """Two-courier assignment request for testing."""
    return AssignmentRequest(
        order_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        restaurant_location=Location(lat=55.6761, lng=12.5683),
        delivery_location=Location(lat=55.6800, lng=12.5900),
        order_total=150.0,
        items_count=3,
        couriers=[
            CourierCandidate(
                courier_id="11111111-1111-1111-1111-111111111111",
                current_location=Location(lat=55.6770, lng=12.5700),
                vehicle_type="bicycle",
                rating=4.5,
                active_deliveries=1,
            ),
            CourierCandidate(
                courier_id="22222222-2222-2222-2222-222222222222",
                current_location=Location(lat=55.7000, lng=12.6200),
                vehicle_type="car",
                rating=4.0,
                active_deliveries=3,
            ),
        ],
    )
