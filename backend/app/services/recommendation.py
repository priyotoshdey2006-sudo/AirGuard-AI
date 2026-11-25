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
        """Fetch live environmental forecast curve and generate personalized plan."""
        raw_data = await open_meteo_service.get_raw_air_quality(request.latitude, request.longitude)
        current = raw_data.get("current", {})
        
        # Extract PM2.5 or proxy AQI
        pm2_5_val = current.get("pm2_5", 35.0)
        current_aqi = int(pm2_5_val * 2.0) if pm2_5_val else 50

        hourly = raw_data.get("hourly", {})
        times = hourly.get("time", [])[:24]
        pm2_5_series = hourly.get("pm2_5", [])[:24]

        hourly_samples = [
            {"time": times[i], "pm2_5": pm2_5_series[i], "aqi_us": int((pm2_5_series[i] or 25.0) * 2.0)}
            for i in range(min(len(times), len(pm2_5_series)))
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
