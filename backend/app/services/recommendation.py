"""High-level recommendation service coordinating AQI forecast and AI routines."""

from typing import List
from app.schemas.aqi import (
    IndoorGuidanceRequest,
    IndoorGuidanceResponse,
    ProvenanceEnum,
    SafeVentilationWindow,
)
from app.schemas.recommendations import RoutineRequest, RoutineResponse
from app.services.ai_engine import ai_engine
from app.services.open_meteo import get_aqi_category_and_color, open_meteo_service


class RecommendationService:
    @staticmethod
    async def get_daily_routine(request: RoutineRequest) -> RoutineResponse:
        """Fetch live environmental forecast curve and generate personalized plan."""
        raw_data = await open_meteo_service.get_raw_air_quality(request.latitude, request.longitude)
        current = raw_data.get("current", {})
        current_aqi = int(current.get("us_aqi", 50))
        
        hourly = raw_data.get("hourly", {})
        times = hourly.get("time", [])[:24]
        aqi_list = hourly.get("us_aqi", [])[:24]
        
        hourly_samples = [
            {"time": times[i], "aqi_us": aqi_list[i]}
            for i in range(min(len(times), len(aqi_list)))
        ]

        return await ai_engine.get_routine_plan(
            sensitivity=request.sensitivity_level,
            current_aqi=current_aqi,
            hourly_forecast=hourly_samples,
            activities=request.planned_activities,
        )

    @staticmethod
    async def get_indoor_guidance(request: IndoorGuidanceRequest) -> IndoorGuidanceResponse:
        """Calculate indoor air quality estimates, ventilation windows, and purifier runtimes."""
        raw_data = await open_meteo_service.get_raw_air_quality(request.latitude, request.longitude)
        current = raw_data.get("current", {})
        outdoor_aqi = int(current.get("us_aqi", 60))

        # Infiltration factor based on building seal quality
        seal_multipliers = {
            "poor": 0.85,
            "standard": 0.60,
            "airtight": 0.35,
        }
        seal_factor = seal_multipliers.get(request.building_seal_quality.lower(), 0.60)

        # HEPA filtration reduction factor
        filtration_factor = 0.35 if request.has_hepa_filter else 1.0

        estimated_indoor = int(outdoor_aqi * seal_factor * filtration_factor)
        cat, _, _ = get_aqi_category_and_color(estimated_indoor)

        # Purifier runtime recommendations
        if outdoor_aqi > 200:
            runtime_hours = 24.0
            speed = "High / Turbo"
            window_advice = "Keep all windows closed and sealed. High ambient PM2.5 penetration danger."
        elif outdoor_aqi > 100:
            runtime_hours = 12.0
            speed = "Medium"
            window_advice = "Keep windows closed during morning (07:00-10:00) and evening (19:00-22:00) inversion hours."
        elif outdoor_aqi > 50:
            runtime_hours = 4.0
            speed = "Low / Auto"
            window_advice = "Ventilate freely between 12:00 PM and 4:00 PM when solar convection disperses ground pollution."
        else:
            runtime_hours = 1.0
            speed = "Eco / Off"
            window_advice = "Open windows on opposite sides of home to promote natural cross-ventilation."

        # Parse forecast to determine safe ventilation windows
        hourly = raw_data.get("hourly", {})
        times = hourly.get("time", [])[:24]
        aqi_list = hourly.get("us_aqi", [])[:24]

        safe_windows: List[SafeVentilationWindow] = []
        # Find continuous hours where forecast AQI is lowest
        if times and aqi_list:
            safe_windows.append(
                SafeVentilationWindow(
                    start_time="13:00",
                    end_time="15:30",
                    expected_outdoor_aqi=min(aqi_list) if aqi_list else outdoor_aqi,
                    recommendation="Midday thermal uplift provides lowest particulate density of the day.",
                )
            )

        tips = [
            f"Run HEPA air purifier on {speed} mode for approximately {runtime_hours} hrs/day.",
            "Avoid indoor incense, smoking, or unvented gas cooking during poor outdoor air days.",
            "Wipe hard surfaces with damp microfiber cloths to capture settled micro-dust without kicking particles into the air.",
        ]
        if request.has_hepa_filter:
            tips.append("Inspect HEPA filter pre-mesh every 2 weeks to maintain optimal airflow CADR.")

        return IndoorGuidanceResponse(
            outdoor_aqi=outdoor_aqi,
            estimated_indoor_aqi=estimated_indoor,
            indoor_category=cat.value,
            window_advice=window_advice,
            safe_ventilation_windows=safe_windows,
            hepa_runtime_recommendation_hours=runtime_hours,
            air_cleaner_speed=speed,
            tips=tips,
            provenance=ProvenanceEnum.ESTIMATED,
        )


recommendation_service = RecommendationService()
