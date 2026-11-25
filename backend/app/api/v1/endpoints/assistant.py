"""Conversational AI Assistant endpoint grounded in local atmospheric facts."""

from fastapi import APIRouter
from app.schemas.assistant import ChatRequest, ChatResponse, ContextData
from app.services.ai_engine import ai_engine
from app.services.open_meteo import open_meteo_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["AI Assistant"])
async def chat_with_copilot(payload: ChatRequest):
    """Interact with AirGuard Copilot. Injects grounded atmospheric metrics to eliminate hallucinations."""
    lat = payload.latitude or 28.6139
    lon = payload.longitude or 77.2090

    # 1. If client already supplied active, verified dashboard metrics, use them directly
    if payload.current_aqi is not None:
        context = ContextData(
            location=payload.location_name or f"Area ({round(lat, 2)}, {round(lon, 2)})",
            current_aqi=payload.current_aqi,
            category=payload.category or "Moderate",
            dominant_pollutant=payload.dominant_pollutant or "pm2_5",
            sensitivity_profile=payload.sensitivity_level or "NORMAL",
            is_live_data_available=True,
        )
    else:
        # 2. Fetch live grounded atmospheric metrics from Open-Meteo model service
        try:
            aqi_data = await open_meteo_service.get_current_aqi(lat, lon)
            
            # Safely extract from US EPA or CPCB model proxy schemas
            aqi_val = None
            category_val = "Moderate"
            dominant_val = "pm2_5"

            if aqi_data.us_epa_model_proxy and aqi_data.us_epa_model_proxy.proxy_index is not None:
                aqi_val = aqi_data.us_epa_model_proxy.proxy_index
                category_val = aqi_data.us_epa_model_proxy.category or "Moderate"
                dominant_val = aqi_data.us_epa_model_proxy.dominant_pollutant or "pm2_5"
            elif aqi_data.cpcb_model_proxy and aqi_data.cpcb_model_proxy.proxy_index is not None:
                aqi_val = aqi_data.cpcb_model_proxy.proxy_index
                category_val = aqi_data.cpcb_model_proxy.category or "Moderate"
                dominant_val = aqi_data.cpcb_model_proxy.dominant_pollutant or "pm2_5"

            loc_name = payload.location_name or aqi_data.location.timezone or f"Area ({round(lat, 2)}, {round(lon, 2)})"

            context = ContextData(
                location=loc_name,
                current_aqi=aqi_val,
                category=category_val,
                dominant_pollutant=dominant_val,
                sensitivity_profile=payload.sensitivity_level or "NORMAL",
                is_live_data_available=aqi_val is not None,
            )
        except Exception:
            # If live model telemetry is unreachable, communicate unavailability honestly. Never fabricate numbers.
            context = ContextData(
                location=payload.location_name or f"Area ({round(lat, 2)}, {round(lon, 2)})",
                current_aqi=None,
                category="Unavailable",
                dominant_pollutant="unknown",
                sensitivity_profile=payload.sensitivity_level or "NORMAL",
                is_live_data_available=False,
            )

    return await ai_engine.get_assistant_chat(payload.message, context)
