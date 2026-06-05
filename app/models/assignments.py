from uuid import UUID

from pydantic import BaseModel


class Location(BaseModel):
    """Geographic coordinates."""

    lat: float
    lng: float


class CourierCandidate(BaseModel):
    """Courier data sent by courier-service for scoring."""

    courier_id: UUID
    current_location: Location
    vehicle_type: str
    rating: float
    active_deliveries: int


class AssignmentRequest(BaseModel):
    """Input for the assignment scoring endpoint."""

    order_id: UUID
    restaurant_location: Location
    delivery_location: Location
    order_total: float
    items_count: int
    couriers: list[CourierCandidate]


class CourierRanking(BaseModel):
    """Scored courier with ETA and reasoning."""

    courier_id: UUID
    score: float
    estimated_delivery_minutes: int
    reasoning: str


class AssignmentResponse(BaseModel):
    """Ranked list of couriers for an order."""

    order_id: UUID
    rankings: list[CourierRanking]
