"""High-level recommendation service coordinating AQI forecast and AI routines."""

from typing import Any, Dict, List
from app.schemas.aqi import ProvenanceEnum
from app.schemas.recommendations import RoutineRequest, RoutineResponse
from app.services.ai_engine import ai_engine
from app.services.indoor_estimator import calculate_indoor_screening
from app.services.open_meteo import get_aqi_category_and_color, open_meteo_service


class RecommendationService:
    @staticmethod
    async def get_daily_routine(request: RoutineRequest) -> RoutineResponse:
        """Fetch live environmental forecast curve and generate personalized plan grounded in verified model metrics."""
        # Retrieve verified current atmospheric analysis
        aqi_data = await open_meteo_service.get_current_aqi(lat=request.latitude, lon=request.longitude)
        current_aqi = (
            aqi_data.us_epa_model_proxy.proxy_index
            if aqi_data.us_epa_model_proxy and aqi_data.us_epa_model_proxy.proxy_index is not None
            else (
                aqi_data.cpcb_model_proxy.proxy_index
                if aqi_data.cpcb_model_proxy and aqi_data.cpcb_model_proxy.proxy_index is not None
                else 50
            )
        )

        # Retrieve verified 24-hour diurnal forecast trajectory
        forecast_data = await open_meteo_service.get_forecast(lat=request.latitude, lon=request.longitude)
        hourly_samples = [
            {
                "time": item.time_local,
                "pm2_5": item.pm2_5,
                "aqi_us": item.us_proxy_index or item.cpcb_proxy_index or current_aqi,
                "category": item.category,
            }
            for item in forecast_data.forecast_series[:24]
        ]

        return await ai_engine.get_routine_plan(
            sensitivity=request.sensitivity_level,
            current_aqi=current_aqi,
            hourly_forecast=hourly_samples,
            activities=request.planned_activities,
        )

    @staticmethod
    async def get_indoor_guidance(
        latitude: float,
        longitude: float,
        room_area_sqm: float = 25.0,
        ceiling_height_m: float = 2.6,
        purifier_cadr_m3h: float = 250.0,
    ) -> Dict[str, Any]:
        """Convenience delegation to the updated mass-balance indoor screening calculator."""
        aqi_data = await open_meteo_service.get_current_aqi(lat=latitude, lon=longitude)
        c_out = aqi_data.pollutants.pm2_5.concentration or 45.0
        return calculate_indoor_screening(
            outdoor_pm2_5=c_out,
            room_area_sqm=room_area_sqm,
            ceiling_height_m=ceiling_height_m,
            purifier_cadr_m3h=purifier_cadr_m3h,
        )


recommendation_service = RecommendationService()
