"""End-to-end verification of core product workflows in AirGuard AI."""

import pytest
from unittest.mock import patch
from app.schemas.recommendations import RoutineRequest
from app.schemas.assistant import ChatRequest, ContextData
from app.services.ai_engine import ai_engine
from app.services.indoor_estimator import calculate_indoor_screening
from app.services.cpcb_calculator import calculate_cpcb_model_proxy
from app.services.epa_calculator import calculate_epa_model_proxy
from app.services.who_comparator import evaluate_who_benchmarks


def test_workflow_1_aqi_dashboard_and_provenance():
    """Verify Dashboard calculates both CPCB and EPA model proxies with strict provenance."""
    pm25 = 90.0
    pm10 = 150.0
    no2 = 60.0

    cpcb = calculate_cpcb_model_proxy(pm2_5=pm25, pm10=pm10, no2=no2)
    epa = calculate_epa_model_proxy(pm2_5=pm25, pm10=pm10, no2=no2)
    who = evaluate_who_benchmarks({"pm2_5": pm25, "pm10": pm10, "no2": no2})

    # CPCB proxy index calculation
    assert cpcb["proxy_index"] == 200
    assert cpcb["category"] == "Moderate"
    assert cpcb["dominant_pollutant"] == "pm2_5"

    # US EPA proxy index calculation (90 ug/m3 is in the 151-200 Unhealthy range)
    assert epa["proxy_index"] is not None
    assert epa["proxy_index"] > 150
    assert epa["category"] == "Unhealthy"

    # WHO guideline comparison (PM2.5 benchmark is 15 ug/m3 24h)
    eval_map = {e["pollutant"]: e for e in who}
    assert eval_map["pm2_5"]["ratio_to_24h_benchmark"] == 6.0  # 90 / 15 = 6.0x
    assert eval_map["pm2_5"]["comparison_status"] == "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"


def test_workflow_2_daily_planner_sensitivity_customization():
    """Verify Daily Planner personalizes safety ratings and mask guidance based on sensitivity profile."""
    # Test Asthmatic profile
    asthmatic_plan = ai_engine.expert.generate_routine(
        sensitivity="ASTHMATIC",
        current_aqi=154,
        hourly_forecast=[{"time": "2026-11-25T10:00", "aqi_us": 154, "pm2_5": 65.0}],
        activities=["Outdoor Morning Jog", "Office Commute"],
    )
    assert asthmatic_plan.sensitivity_level == "ASTHMATIC"
    assert "High" in asthmatic_plan.overall_risk_assessment
    jog_window = next(w for w in asthmatic_plan.activity_windows if "Jog" in w.activity_name)
    assert jog_window.safety_rating == "AVOID"
    assert jog_window.mask_recommendation == "N95_REQUIRED"

    # Test Normal healthy profile under same conditions
    normal_plan = ai_engine.expert.generate_routine(
        sensitivity="NORMAL",
        current_aqi=154,
        hourly_forecast=[{"time": "2026-11-25T10:00", "aqi_us": 154, "pm2_5": 65.0}],
        activities=["Outdoor Morning Jog", "Office Commute"],
    )
    assert normal_plan.sensitivity_level == "NORMAL"
    assert normal_plan.activity_windows[0].mask_recommendation in ["N95_REQUIRED", "SURGICAL"]


def test_workflow_3_indoor_guidance_physics():
    """Verify Indoor Guidance mass-balance box model calculates infiltration and purifier impact."""
    # Room: 25 sqm (approx 270 sqft), 2.6m ceiling = 65 m3
    res_with_hepa = calculate_indoor_screening(
        outdoor_pm2_5=90.0,
        room_area_sqm=25.0,
        ceiling_height_m=2.6,
        purifier_cadr_m3h=250.0,
    )
    res_no_hepa = calculate_indoor_screening(
        outdoor_pm2_5=90.0,
        room_area_sqm=25.0,
        ceiling_height_m=2.6,
        purifier_cadr_m3h=0.0,
    )

    # CADR purifier should provide ~3.85 ACH
    assert abs(res_with_hepa["purifier_engineering_estimate"]["equivalent_ach"] - 3.85) < 0.1

    # Infiltration with HEPA reduces steady-state particulate concentration substantially
    fav_hepa = res_with_hepa["scenario_based_heuristic_estimates"]["favorable_envelope_scenario_ug_m3"]
    fav_no_hepa = res_no_hepa["scenario_based_heuristic_estimates"]["favorable_envelope_scenario_ug_m3"]
    assert fav_hepa < fav_no_hepa
    assert fav_hepa < 10.0  # Safe indoor level


def test_workflow_4_copilot_assistant_consistency():
    """Verify AI Copilot uses exact Dashboard AQI context (154) and does NOT return 75."""
    context = ContextData(
        location="Delhi Central",
        current_aqi=154,
        category="Unhealthy",
        dominant_pollutant="pm2_5",
        sensitivity_profile="ASTHMATIC",
        is_live_data_available=True,
    )

    reply = ai_engine.expert.generate_chat_reply("Should I wear an N95 mask outside?", context)
    assert reply.context_used.current_aqi == 154
    assert reply.context_used.category == "Unhealthy"
    assert "154" in reply.reply
    assert "75" not in reply.reply
    assert "N95 or FFP2 respirator" in reply.reply


def test_workflow_5_error_and_unavailable_telemetry_graceful_handling():
    """Verify that when live telemetry is unavailable, Zero-Fabrication protocol is strictly respected."""
    context = ContextData(
        location="Unknown Station",
        current_aqi=None,
        category="Unavailable",
        dominant_pollutant="unknown",
        sensitivity_profile="NORMAL",
        is_live_data_available=False,
    )

    reply = ai_engine.expert.generate_chat_reply("What is my current AQI?", context)
    assert reply.context_used.current_aqi is None
    assert reply.context_used.is_live_data_available is False
    assert "unavailable" in reply.reply.lower()
    assert "Zero-Fabrication Policy" in reply.reply
    assert "75" not in reply.reply
