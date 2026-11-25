"""Root Integration Smoke Test Suite for AirGuard AI Platform.

Verifies end-to-end functionality across all core services:
1. Root operational status (GET /)
2. Health & Liveness probes (GET /health, GET /api/v1/health, GET /api/v1/health/db)
3. Current AQI retrieval with CPCB/EPA model proxies (GET /api/v1/aqi/current)
4. 24-Hour hourly forecast series (GET /api/v1/aqi/forecast)
5. Indoor air quality box model screening (POST & GET /api/v1/indoor/screening)
6. Personalized daily routine planner (POST /api/v1/recommendations/routine)
7. Eco-commute sustainable route comparison (POST /api/v1/transport/compare)
8. Community hazard reporting & upvoting (POST & GET /api/v1/community/reports)
9. Grounded AI Environmental Copilot (POST /api/v1/assistant/chat)
"""

import sys
import os
import pytest
from starlette.testclient import TestClient
import httpx

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from app.services.open_meteo import open_meteo_service, _CACHE

MOCK_METEO_PAYLOAD = {
    "latitude": 28.625,
    "longitude": 77.25,
    "utc_offset_seconds": 19800,
    "timezone": "Asia/Kolkata",
    "timezone_abbreviation": "IST",
    "elevation": 216.0,
    "current": {
        "time": "2026-11-24T10:00",
        "interval": 3600,
        "pm10": 160.0,
        "pm2_5": 95.0,
        "carbon_monoxide": 880.0,
        "nitrogen_dioxide": 65.0,
        "sulphur_dioxide": 14.0,
        "ozone": 40.0,
        "uv_index": 3.5,
    },
    "hourly": {
        "time": [f"2026-11-24T{h:02d}:00" for h in range(24)],
        "pm10": [160.0] * 24,
        "pm2_5": [95.0] * 24,
        "carbon_monoxide": [880.0] * 24,
        "nitrogen_dioxide": [65.0] * 24,
        "sulphur_dioxide": [14.0] * 24,
        "ozone": [40.0] * 24,
        "uv_index": [3.5] * 24,
    },
}


@pytest.fixture(autouse=True)
def setup_mock_open_meteo():
    """Ensure Open-Meteo external calls return controlled telemetry without network dependency."""
    _CACHE.clear()

    def mock_handler(request: httpx.Request):
        return httpx.Response(200, json=MOCK_METEO_PAYLOAD)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    open_meteo_service._client = mock_client
    yield
    open_meteo_service._client = None
    _CACHE.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_root_and_health_endpoints(client):
    """Test root and liveness endpoints."""
    # 1. Root
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "operational"
    assert res.json()["project"] == "AirGuard AI"

    # 2. Root Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
    assert res_health.json()["version"] == "1.0.0"

    # 3. API v1 Health
    res_v1 = client.get("/api/v1/health")
    assert res_v1.status_code == 200
    assert res_v1.json()["status"] == "online"
    assert res_v1.json()["service"] == "AirGuard AI Engine"

    # 4. API v1 DB Health
    res_db = client.get("/api/v1/health/db")
    assert res_db.status_code == 200
    assert res_db.json()["status"] in ["ready", "unavailable"]


def test_current_aqi_and_provenance(client):
    """Test retrieval of current AQI and ensure provenance compliance."""
    res = client.get("/api/v1/aqi/current?lat=28.6139&lon=77.2090")
    assert res.status_code == 200
    data = res.json()

    assert data["location"]["latitude"] == 28.6139
    assert data["location"]["longitude"] == 77.2090

    # Data provenance check
    prov = data["provenance"]
    assert prov["native_atmospheric_model"] == "ECMWF CAMS Global (IFS-AER)"
    assert prov["is_ground_observation"] is False

    # CPCB & EPA proxies
    assert "cpcb_model_proxy" in data
    assert data["cpcb_model_proxy"]["proxy_index"] > 0
    assert "us_epa_model_proxy" in data
    assert data["us_epa_model_proxy"]["proxy_index"] > 0


def test_forecast_aqi_endpoint(client):
    """Test 24-hour forecast endpoint."""
    res = client.get("/api/v1/aqi/forecast?lat=28.6139&lon=77.2090")
    assert res.status_code == 200
    data = res.json()
    assert "forecast_series" in data
    assert len(data["forecast_series"]) == 24
    assert data["forecast_series"][0]["cpcb_proxy_index"] > 0


def test_indoor_screening_endpoint(client):
    """Test indoor single-zone box model screening calculation."""
    payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "room_area_sqm": 30.0,
        "ceiling_height_m": 2.8,
        "purifier_cadr_m3h": 320.0,
    }
    res = client.post("/api/v1/indoor/screening", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["outdoor_ambient_pm2_5"] == 95.0
    assert "scenario_based_heuristic_estimates" in data
    assert "purifier_engineering_estimate" in data
    assert data["purifier_engineering_estimate"]["equivalent_ach"] > 0


def test_routine_recommendation_endpoint(client):
    """Test personalized daily routine planning with activity scheduling."""
    payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "sensitivity_level": "ASTHMATIC",
        "planned_activities": ["Morning Jog", "Commute to Work", "Evening Walk"],
    }
    res = client.post("/api/v1/recommendations/daily-routine", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "activity_windows" in data
    assert len(data["activity_windows"]) > 0
    assert "action_items" in data
    assert "daily_summary" in data


def test_transport_comparison_endpoint(client):
    """Test sustainable alternative transit comparison with emissions & dose."""
    payload = {
        "origin_name": "Connaught Place",
        "dest_name": "Cyber Hub Gurgaon",
        "origin_lat": 28.6315,
        "origin_lon": 77.2167,
        "dest_lat": 28.4950,
        "dest_lon": 77.0895,
    }
    res = client.post("/api/v1/transport/compare-routes", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "options" in data
    assert len(data["options"]) >= 3
    metro = next((m for m in data["options"] if "METRO" in m["mode"]), None)
    ice_car = next((m for m in data["options"] if "ICE_CAR" in m["mode"] or "CAR" in m["mode"]), None)
    if metro and ice_car:
        assert metro["co2_kg"] < ice_car["co2_kg"]



def test_community_reports_flow(client):
    """Test reporting a hazard and fetching reports."""
    new_report = {
        "title": "Stubble burning smoke along outer ring road",
        "description": "Dense smoke causing extreme reduction in visibility and sharp burning smell.",
        "category": "BIOMASS_BURNING",
        "severity": 4,
        "latitude": 28.7041,
        "longitude": 77.1025,
        "reporter_name": "Rohini Resident",
    }
    create_res = client.post("/api/v1/community/reports", json=new_report)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # Fetch reports
    list_res = client.get("/api/v1/community/reports?lat=28.7041&lon=77.1025&radius_km=25")
    assert list_res.status_code == 200
    reports = list_res.json()["reports"]
    assert any(r["id"] == created_id for r in reports)

    # Upvote
    upvote_res = client.post(f"/api/v1/community/reports/{created_id}/upvote")
    assert upvote_res.status_code == 200
    assert upvote_res.json()["upvotes_count"] >= 1


def test_ai_copilot_chat_endpoint(client):
    """Test AI Environmental Copilot grounded chat response."""
    payload = {
        "message": "Should my elderly father wear an N95 mask today during his morning walk?",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "sensitivity": "ELDERLY",
    }
    res = client.post("/api/v1/assistant/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert "model_provider" in data
