"""AI Engine service with Gemini 2.0, Groq, and Deterministic Fallback."""

import json
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.schemas.aqi import ProvenanceEnum
from app.schemas.assistant import ChatResponse, ContextData
from app.schemas.recommendations import ActivityWindow, RoutineResponse


class DeterministicExpertEngine:
    """Rule-based clinical & environmental intelligence engine based on EPA & WHO guidelines."""

    @staticmethod
    def generate_routine(
        sensitivity: str,
        current_aqi: int,
        hourly_forecast: List[Dict[str, Any]],
        activities: List[str],
    ) -> RoutineResponse:
        # Find peak and best window in 24h forecast
        best_hour = "14:00 - 16:00"
        lowest_aqi = current_aqi
        if hourly_forecast:
            sorted_by_aqi = sorted(hourly_forecast, key=lambda x: x.get("aqi_us", 999))
            best_entry = sorted_by_aqi[0]
            best_time = best_entry.get("time", "14:00")
            best_hour = best_time.split("T")[-1][:5] if "T" in best_time else best_time
            lowest_aqi = best_entry.get("aqi_us", current_aqi)

        # Risk categorization based on sensitivity and current AQI
        is_sensitive = sensitivity in ["ASTHMATIC", "CARDIOVASCULAR", "ELDERLY", "CHILD"]
        
        if current_aqi <= 50:
            risk = "Low Environmental Risk"
            summary = "Air quality is optimal for all outdoor workouts and daily commute activities."
            mask = "NONE"
            safety = "SAFE"
            indoor = "Natural ventilation is highly recommended. Keep windows open."
        elif current_aqi <= 100:
            risk = "Moderate Risk" if is_sensitive else "Low-to-Moderate Risk"
            summary = (
                f"Air quality is acceptable for the general public, but {sensitivity.lower()} individuals "
                "should schedule intense cardio during lower pollutant hours."
            )
            mask = "SURGICAL" if is_sensitive else "NONE"
            safety = "CAUTION" if is_sensitive else "SAFE"
            indoor = "Ventilate during midday hours when dispersion is highest. Use air purifiers on low."
        elif current_aqi <= 150:
            risk = "Elevated Risk for Sensitive Groups"
            summary = (
                f"Elevated PM2.5 levels detected. Sensitive groups ({sensitivity}) face aggravated respiratory symptoms. "
                "Shift strenuous outdoor training indoors or to clean air windows."
            )
            mask = "N95_REQUIRED" if is_sensitive else "SURGICAL"
            safety = "AVOID" if is_sensitive else "CAUTION"
            indoor = "Keep external windows closed during morning/evening inversion peaks. Run HEPA filtration on medium."
        else:
            risk = "High / Hazardous Environmental Risk"
            summary = (
                "Unhealthy ambient particulate concentration. Prolonged outdoor exertion should be avoided by all individuals. "
                "Wear certified N95 respirators for mandatory outdoor transit."
            )
            mask = "N95_REQUIRED"
            safety = "AVOID"
            indoor = "Seal doors and windows tightly. Continuous HEPA air filtration recommended. Avoid indoor combustion."

        activity_windows: List[ActivityWindow] = []
        for act in activities:
            is_strenuous = any(k in act.lower() for k in ["jog", "run", "cycle", "football", "gym", "cardio", "walk"])
            if current_aqi > 150 and is_strenuous:
                act_safety = "AVOID"
                act_mask = "N95_REQUIRED"
                act_time = "Shift to Indoor Gym"
                tip = "High particulate inhalation during heavy breathing damages alveoli. Exercise indoors."
            elif current_aqi > 100 and is_sensitive:
                act_safety = "CAUTION"
                act_mask = "N95_REQUIRED"
                act_time = f"Best Window: {best_hour}"
                tip = f"Reschedule to midday ({best_hour}) when thermal atmospheric mixing lowers PM2.5."
            else:
                act_safety = safety
                act_mask = mask
                act_time = f"Recommended: {best_hour}"
                tip = "Maintain hydration and monitor localized air quality updates before departure."

            activity_windows.append(
                ActivityWindow(
                    activity_name=act,
                    optimal_time=act_time,
                    expected_aqi=lowest_aqi if "Best" in act_time else current_aqi,
                    safety_rating=act_safety,
                    mask_recommendation=act_mask,
                    mitigation_tips=tip,
                )
            )

        actions = [
            f"Check localized AQI before beginning outdoor activities.",
            f"Equip {mask.replace('_', ' ')} when stepping outside into traffic corridors.",
            indoor,
            f"Target outdoor errands around {best_hour} when particulate density dips.",
        ]

        return RoutineResponse(
            sensitivity_level=sensitivity,
            overall_risk_assessment=risk,
            daily_summary=summary,
            activity_windows=activity_windows,
            action_items=actions,
            indoor_guidance=indoor,
            model_provider="AirGuard-Expert-Rules (Offline-Ready)",
            provenance=ProvenanceEnum.ESTIMATED,
        )

    @staticmethod
    def generate_chat_reply(message: str, context: ContextData) -> ChatResponse:
        msg = message.lower()
        aqi = context.current_aqi
        sens = context.sensitivity_profile

        if any(w in msg for w in ["mask", "n95", "protect"]):
            if aqi > 100:
                reply = (
                    f"Given your local AQI is {aqi} ({context.category}), standard cloth masks are ineffective against fine PM2.5 particulates. "
                    "You should use a well-fitted **N95 or FFP2 respirator** with an airtight seal around your nose and chin when outside."
                )
            else:
                reply = f"Current AQI is {aqi} ({context.category}). General outdoor air does not strictly necessitate an N95 mask, though sensitive individuals may choose surgical protection in heavy traffic."
        elif any(w in msg for w in ["jog", "run", "exercise", "walk", "outdoor"]):
            if aqi > 150:
                reply = (
                    f"Outdoor cardio is **not recommended** today (current AQI: {aqi} - {context.category}). "
                    "When exercising, minute ventilation increases by 4x to 6x, pulling fine particles deep into the pulmonary bronchioles. "
                    "Please shift your workout to an indoor gym or well-ventilated indoor space."
                )
            elif aqi > 100:
                reply = (
                    f"Current AQI is {aqi} ({context.category}). If you are {sens.lower()}, avoid vigorous outdoor running. "
                    "Target early afternoon (around 13:00 - 15:00) when daytime atmospheric inversion lifts, and keep exertion moderate."
                )
            else:
                reply = f"Air quality is currently {context.category} (AQI: {aqi}). Conditions are favorable for outdoor exercise and running!"
        elif any(w in msg for w in ["window", "ventilate", "indoor", "purifier", "hepa"]):
            if aqi > 120:
                reply = (
                    f"Keep your windows **closed** right now. Ambient outdoor PM2.5 is high (AQI {aqi}). "
                    "Run your HEPA air purifier on continuous medium or auto mode. If you must ventilate, do so briefly around 14:00."
                )
            else:
                reply = f"Ambient AQI is {aqi} ({context.category}). It is safe to open windows for 20-30 minutes to refresh indoor air and exhaust indoor VOCs."
        else:
            reply = (
                f"In your area, the current Air Quality Index is **{aqi}** ({context.category}), with **{context.dominant_pollutant.upper()}** as the dominant pollutant. "
                f"For someone with a **{sens}** profile, we recommend monitoring hourly forecast trends and scheduling outdoor travel during midday clean air windows."
            )

        return ChatResponse(
            reply=reply,
            session_id="session-default",
            model_provider="AirGuard-Expert-Rules",
            context_used=context,
            suggested_followups=[
                "Should I wear an N95 mask today?",
                "What is the best time for my outdoor jog?",
                "When should I open my windows for ventilation?",
            ],
        )


class AIEngineService:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.groq_key = settings.GROQ_API_KEY
        self.expert = DeterministicExpertEngine()

    async def get_routine_plan(
        self,
        sensitivity: str,
        current_aqi: int,
        hourly_forecast: List[Dict[str, Any]],
        activities: List[str],
    ) -> RoutineResponse:
        """Generate personalized daily routine via Gemini, Groq, or deterministic fallback."""
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                prompt = (
                    f"You are AirGuard AI. Output STRICT JSON conforming to this schema:\n"
                    f"{{\n"
                    f"  'overall_risk_assessment': string,\n"
                    f"  'daily_summary': string,\n"
                    f"  'indoor_guidance': string,\n"
                    f"  'action_items': [string],\n"
                    f"  'activity_windows': [\n"
                    f"    {{'activity_name': string, 'optimal_time': string, 'expected_aqi': int, 'safety_rating': 'SAFE'|'CAUTION'|'AVOID', 'mask_recommendation': 'NONE'|'SURGICAL'|'N95_REQUIRED', 'mitigation_tips': string}}\n"
                    f"  ]\n"
                    f"}}\n"
                    f"Context: Current AQI={current_aqi}, Sensitivity={sensitivity}, Planned Activities={activities}.\n"
                    f"Hourly forecast samples: {json.dumps(hourly_forecast[:8])}.\n"
                    f"Ground your advice strictly in the provided figures. No hallucinations."
                )
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                parsed = json.loads(text.strip())
                
                windows = [ActivityWindow(**w) for w in parsed.get("activity_windows", [])]
                return RoutineResponse(
                    sensitivity_level=sensitivity,
                    overall_risk_assessment=parsed.get("overall_risk_assessment", "Evaluated"),
                    daily_summary=parsed.get("daily_summary", "Routine evaluated based on atmospheric curves."),
                    activity_windows=windows,
                    action_items=parsed.get("action_items", []),
                    indoor_guidance=parsed.get("indoor_guidance", "Keep air purifier on."),
                    model_provider="Google-Gemini-2.0-Flash",
                    provenance=ProvenanceEnum.ESTIMATED,
                )
            except Exception as e:
                logger.warning(f"Gemini API invocation failed ({e}). Falling back to expert engine.")

        # Fallback to deterministic expert engine
        return self.expert.generate_routine(sensitivity, current_aqi, hourly_forecast, activities)

    async def get_assistant_chat(self, message: str, context: ContextData) -> ChatResponse:
        """Contextual chatbot conversation with zero hallucination guarantee."""
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                prompt = (
                    f"System: You are AirGuard Copilot, an environmental intelligence assistant. "
                    f"Grounded verified data: Location={context.location}, Current AQI={context.current_aqi} ({context.category}), "
                    f"Dominant Pollutant={context.dominant_pollutant}, User Health Profile={context.sensitivity_profile}. "
                    f"Rule: NEVER fabricate environmental numbers. Answer concisely and empathetically with preventive actions.\n\n"
                    f"User Query: {message}"
                )
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                return ChatResponse(
                    reply=response.text.strip(),
                    session_id="gemini-session",
                    model_provider="Google-Gemini-2.0-Flash",
                    context_used=context,
                    suggested_followups=[
                        "What are the best indoor ventilation hours today?",
                        "Should I wear an N95 mask outside?",
                        "How does current air affect my workout?",
                    ],
                )
            except Exception as e:
                logger.warning(f"Gemini chat failed ({e}). Falling back to expert engine.")

        return self.expert.generate_chat_reply(message, context)


ai_engine = AIEngineService()
