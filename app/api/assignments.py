from fastapi import APIRouter

from app.models.assignments import AssignmentRequest, AssignmentResponse
from app.service.assignment_service import score_assignment

router = APIRouter(prefix="/api/v1", tags=["assignments"])


@router.post("/assignments/score", response_model=AssignmentResponse)
async def score_couriers(request: AssignmentRequest) -> AssignmentResponse:
    """Score and rank couriers for an order assignment."""
    return await score_assignment(request)
