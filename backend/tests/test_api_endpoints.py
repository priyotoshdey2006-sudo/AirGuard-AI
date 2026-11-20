"""Direct integration and unit tests for AirGuard AI endpoints and services."""

import asyncio
import pytest
from app.api.v1.endpoints.health import health_check
from app.api.v1.endpoints.aqi import (
    get_current_air_quality,
    get_air_quality_forecast,
    calculate_indoor_guidance,
)
from app.api.v1.endpoints.recommendations import get_daily_routine_recommendation
from app.api.v1.endpoints.transport import compare_transport_modes, log_travel_commute, get_travel_logs
from app.api.v1.endpoints.community import (
    list_community_reports,
    submit_community_report,
    upvote_community_report,
)
from app.api.v1.endpoints.assistant import chat_with_copilot
from app.api.v1.endpoints.auth import register_user, login_user, get_my_profile
from app.schemas.aqi import IndoorGuidanceRequest
from app.schemas.recommendations import RoutineRequest
from app.schemas.transport import RouteCompareRequest, TravelLogCreate
from app.schemas.community import CommunityReportCreate
from app.schemas.assistant import ChatRequest
from app.schemas.user import UserRegister, UserLogin


def test_health_check(db):
    result = health_check(db)
    assert result["status"] == "online"
    assert result["service"] == "AirGuard AI Engine"
    assert result["database"] == "healthy"


def test_current_aqi():
    res = asyncio.run(get_current_air_quality(lat=28.6139, lon=77.2090))
    assert res.aqi_us >= 0
    assert res.pollutants.pm2_5 >= 0.0
    assert res.provenance in ["OBSERVED", "ESTIMATED"]


def test_forecast_aqi():
    res = asyncio.run(get_air_quality_forecast(lat=28.6139, lon=77.2090))
    assert len(res.hourly) > 0
    assert len(res.daily) > 0
    assert res.provenance == "FORECAST"


def test_indoor_guidance():
    payload = IndoorGuidanceRequest(
        latitude=28.6139,
        longitude=77.2090,
        room_sqft=450.0,
        has_hepa_filter=True,
        has_ac=True,
        building_seal_quality="standard",
    )
    res = asyncio.run(calculate_indoor_guidance(payload))
    assert res.outdoor_aqi >= 0
    assert res.estimated_indoor_aqi >= 0
    assert len(res.safe_ventilation_windows) >= 1
    assert res.hepa_runtime_recommendation_hours >= 0


def test_daily_routine_recommendation():
    payload = RoutineRequest(
        latitude=28.6139,
        longitude=77.2090,
        sensitivity_level="ASTHMATIC",
        planned_activities=["Morning Jog", "Commute to Work", "Evening Walk"],
    )
    res = asyncio.run(get_daily_routine_recommendation(payload, current_user=None))
    assert res.sensitivity_level == "ASTHMATIC"
    assert len(res.activity_windows) == 3
    assert len(res.action_items) > 0


def test_route_comparison():
    payload = RouteCompareRequest(
        origin_lat=28.6139,
        origin_lon=77.2090,
        dest_lat=28.5355,
        dest_lon=77.3910,
        origin_name="Connaught Place",
        dest_name="Noida Sector 18",
    )
    res = asyncio.run(compare_transport_modes(payload))
    assert res.distance_km > 0
    assert len(res.options) >= 3
    assert res.total_trees_equivalent >= 0


def test_community_reports_flow(db):
    # 1. Submit report
    create_payload = CommunityReportCreate(
        title="Severe dust near construction site",
        description="Heavy particulate blowing across crossing",
        category="CONSTRUCTION_DUST",
        severity=4,
        latitude=28.6139,
        longitude=77.2090,
        reporter_name="Local Resident",
    )
    created = submit_community_report(create_payload, current_user=None, db=db)
    assert created.id is not None
    assert created.upvotes_count == 1

    # 2. List reports
    listed = list_community_reports(lat=28.6139, lon=77.2090, radius_km=15.0, category="ALL", db=db)
    assert listed.total >= 1

    # 3. Upvote
    upvoted = upvote_community_report(created.id, db=db)
    assert upvoted["upvotes_count"] == 2


def test_assistant_chat():
    payload = ChatRequest(
        message="Should I wear an N95 mask today?",
        latitude=28.6139,
        longitude=77.2090,
        sensitivity_level="ASTHMATIC",
    )
    res = asyncio.run(chat_with_copilot(payload))
    assert len(res.reply) > 10
    assert res.context_used.sensitivity_profile == "ASTHMATIC"


def test_auth_workflow(db):
    # 1. Register
    reg_payload = UserRegister(
        email="citizen@airguard.ai",
        password="secretpassword123",
        full_name="Jane Doe",
        sensitivity_level="ASTHMATIC",
    )
    token = register_user(reg_payload, db=db)
    assert token.access_token is not None

    # 2. Login
    login_payload = UserLogin(
        email="citizen@airguard.ai",
        password="secretpassword123",
    )
    token_login = login_user(login_payload, db=db)
    assert token_login.access_token is not None

    # 3. Log commute
    log_payload = TravelLogCreate(
        mode="BICYCLE",
        origin_name="Home",
        destination_name="Office",
        distance_km=8.5,
        duration_minutes=35.0,
        avg_aqi_exposure=60.0,
        co2_emitted_kg=0.0,
        co2_saved_kg=1.45,
    )
    saved_log = log_travel_commute(log_payload, current_user=None, db=db)
    assert saved_log.id is not None
    assert saved_log.co2_saved_kg == 1.45

    logs = get_travel_logs(current_user=None, db=db)
    assert len(logs) >= 1
