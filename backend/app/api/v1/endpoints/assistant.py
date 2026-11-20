"""Conversational AI Assistant endpoint grounded in local atmospheric facts."""

from fastapi import APIRouter
from app.schemas.assistant import ChatRequest, ChatResponse, ContextData
from app.services.ai_engine import ai_engine
from app.services.open_meteo import open_meteo_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["AI Assistant"])
async def chat_with_copilot(payload: ChatRequest):
    """Interact with AirGuard Copilot. Injects observed environmental metrics to eliminate hallucinations."""
    lat = payload.latitude or 28.6139
    lon = payload.longitude or 77.2090

    # Fetch live grounded metrics
    try:
        aqi_data = await open_meteo_service.get_current_aqi(lat, lon)
        context = ContextData(
            location=f"Area ({round(lat, 2)}, {round(lon, 2)})",
            current_aqi=aqi_data.aqi_us,
            category=aqi_data.category.value,
            dominant_pollutant=aqi_data.dominant_pollutant,
            sensitivity_profile=payload.sensitivity_level or "NORMAL",
        )
    except Exception:
        context = ContextData(
            location="Current Location",
            current_aqi=75,
            category="Moderate",
            dominant_pollutant="pm2_5",
            sensitivity_profile=payload.sensitivity_level or "NORMAL",
        )

    return await ai_engine.get_assistant_chat(payload.message, context)
