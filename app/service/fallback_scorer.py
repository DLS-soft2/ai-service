import math

from app.models.assignments import AssignmentRequest, CourierRanking, Location


def haversine_km(loc1: Location, loc2: Location) -> float:
    """Calculate the great-circle distance between two points in kilometres."""
    r = 6371.0
    lat1, lat2 = math.radians(loc1.lat), math.radians(loc2.lat)
    dlat = math.radians(loc2.lat - loc1.lat)
    dlng = math.radians(loc2.lng - loc1.lng)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def score_couriers_by_distance(request: AssignmentRequest) -> list[CourierRanking]:
    """Deterministic scoring based on distance, rating, and active deliveries."""
    rankings: list[CourierRanking] = []
    for courier in request.couriers:
        distance_km = haversine_km(courier.current_location, request.restaurant_location)
        distance_score = max(0.0, 1.0 - distance_km / 20.0) * 0.5
        rating_score = (courier.rating / 5.0) * 0.3
        load_score = max(0.0, 1.0 - courier.active_deliveries / 5.0) * 0.2
        score = round(min(1.0, distance_score + rating_score + load_score), 4)
        eta = max(1, round(distance_km * 3 + 10 + courier.active_deliveries * 5))
        reasoning = (
            f"Distance: {distance_km:.1f}km, Rating: {courier.rating}, "
            f"Active deliveries: {courier.active_deliveries}"
        )
        rankings.append(CourierRanking(
            courier_id=courier.courier_id,
            score=score,
            estimated_delivery_minutes=eta,
            reasoning=reasoning,
        ))
    rankings.sort(key=lambda r: r.score, reverse=True)
    return rankings
