from app.models.assignments import AssignmentRequest, CourierCandidate, Location
from app.service.fallback_scorer import haversine_km, score_couriers_by_distance


def test_deterministic_same_input_same_output(sample_request):
    result1 = score_couriers_by_distance(sample_request)
    result2 = score_couriers_by_distance(sample_request)
    assert result1 == result2


def test_closer_courier_scores_higher():
    close = CourierCandidate(
        courier_id="11111111-1111-1111-1111-111111111111",
        current_location=Location(lat=55.676, lng=12.569),
        vehicle_type="bicycle", rating=4.0, active_deliveries=1,
    )
    far = CourierCandidate(
        courier_id="22222222-2222-2222-2222-222222222222",
        current_location=Location(lat=56.0, lng=13.0),
        vehicle_type="bicycle", rating=4.0, active_deliveries=1,
    )
    request = AssignmentRequest(
        order_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        restaurant_location=Location(lat=55.6761, lng=12.5683),
        delivery_location=Location(lat=55.68, lng=12.59),
        order_total=100.0, items_count=2, couriers=[close, far],
    )
    rankings = score_couriers_by_distance(request)
    assert rankings[0].courier_id == close.courier_id


def test_higher_rated_courier_scores_higher():
    low_rated = CourierCandidate(
        courier_id="11111111-1111-1111-1111-111111111111",
        current_location=Location(lat=55.676, lng=12.569),
        vehicle_type="bicycle", rating=1.0, active_deliveries=1,
    )
    high_rated = CourierCandidate(
        courier_id="22222222-2222-2222-2222-222222222222",
        current_location=Location(lat=55.676, lng=12.569),
        vehicle_type="bicycle", rating=5.0, active_deliveries=1,
    )
    request = AssignmentRequest(
        order_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        restaurant_location=Location(lat=55.6761, lng=12.5683),
        delivery_location=Location(lat=55.68, lng=12.59),
        order_total=100.0, items_count=2, couriers=[low_rated, high_rated],
    )
    rankings = score_couriers_by_distance(request)
    assert rankings[0].courier_id == high_rated.courier_id


def test_scores_between_0_and_1(sample_request):
    rankings = score_couriers_by_distance(sample_request)
    for r in rankings:
        assert 0.0 <= r.score <= 1.0


def test_etas_are_positive_integers(sample_request):
    rankings = score_couriers_by_distance(sample_request)
    for r in rankings:
        assert isinstance(r.estimated_delivery_minutes, int)
        assert r.estimated_delivery_minutes > 0


def test_haversine_known_distance():
    """Copenhagen to Malmo is roughly 28 km."""
    cph = Location(lat=55.6761, lng=12.5683)
    malmo = Location(lat=55.6050, lng=13.0038)
    dist = haversine_km(cph, malmo)
    assert 25 < dist < 35
