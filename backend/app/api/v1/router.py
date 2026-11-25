"""Central API v1 router aggregator."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    aqi,
    assistant,
    auth,
    community,
    health,
    indoor,
    recommendations,
    transport,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(aqi.router, prefix="/aqi", tags=["Air Quality"])
api_router.include_router(indoor.router, prefix="/indoor", tags=["Indoor Air Quality"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["AI Recommendations"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])
api_router.include_router(transport.router, prefix="/transport", tags=["Sustainable Transport"])
api_router.include_router(community.router, prefix="/community", tags=["Community Reports"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
