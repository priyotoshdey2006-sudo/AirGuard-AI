"""Personalized AI daily routine recommendation endpoint."""

from typing import Optional
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user_optional
from app.models.user import User
from app.schemas.recommendations import RoutineRequest, RoutineResponse
from app.services.recommendation import recommendation_service

router = APIRouter()


@router.post("/daily-routine", response_model=RoutineResponse, tags=["AI Recommendations"])
async def get_daily_routine_recommendation(
    payload: RoutineRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Generate structured, health-customized schedule grounded in forecast AQI curves."""
    # If user is authenticated and hasn't explicitly overridden sensitivity, use their profile sensitivity
    if current_user and current_user.profile and payload.sensitivity_level == "NORMAL":
        payload.sensitivity_level = current_user.profile.sensitivity_level

    return await recommendation_service.get_daily_routine(payload)
