"""Integration tests for AirGuard AI REST API endpoints."""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.services.open_meteo import open_meteo_service, _CACHE
import httpx


MOCK_METEO_PAYLOAD = {
    "latitude": 28.625,
    "longitude": 77.25,
    "utc_offset_seconds": 19800,
    "timezone": "Asia/Kolkata",
    "timezone_abbreviation": "IST",
    "elevation": 216.0,
    "current": {
        "time": "2026-11-21T10:00",
        "interval": 3600,
        "pm10": 150.0,
        "pm2_5": 90.0,
        "carbon_monoxide": 850.0,
        "nitrogen_dioxide": 60.0,
        "sulphur_dioxide": 12.0,
        "ozone": 42.0,
        "uv_index": 3.2,
    },
    "hourly": {
        "time": [f"2026-11-21T{h:02d}:00" for h in range(24)],
        "pm10": [150.0] * 24,
        "pm2_5": [90.0] * 24,
        "carbon_monoxide": [850.0] * 24,
        "nitrogen_dioxide": [60.0] * 24,
        "sulphur_dioxide": [12.0] * 24,
        "ozone": [42.0] * 24,
        "uv_index": [3.0] * 24,
    },
}


@pytest.fixture(autouse=True)
def setup_mock_open_meteo():
    """Ensure Open-Meteo calls inside integration tests return controlled mock telemetry without network."""
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


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["project"] == "AirGuard AI"


def test_root_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "AirGuard AI"
    assert "version" in data



def test_health_check_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "AirGuard AI Engine"


def test_get_current_aqi_success(client):
    response = client.get("/api/v1/aqi/current?lat=28.6139&lon=77.2090")
    assert response.status_code == 200
    data = response.json()

    # Provenance
    prov = data["provenance"]
    assert prov["native_atmospheric_model"] == "ECMWF CAMS Global (IFS-AER)"
    assert prov["native_spatial_resolution"] == "0.4° (~45 km)"
    assert prov["native_temporal_resolution"] == "3-hourly"
    assert prov["is_ground_observation"] is False
    assert prov["model_cycle_utc"] is None
    assert prov["model_valid_utc"] == "2026-11-21T10:00:00Z"
    assert prov["model_valid_local"].startswith("2026-11-21T15:30:00+05:30")
    assert prov["retrieved_at_utc"].endswith("Z")

    # CPCB Model Proxy
    cpcb = data["cpcb_model_proxy"]
    assert cpcb["proxy_index"] == 200
    assert cpcb["category"] == "Moderate"
    assert cpcb["dominant_pollutant"] == "pm2_5"
    assert cpcb["index_type"] == "CPCB_BREAKPOINT_BASED_MODEL_PROXY"
    assert "regulatory CPCB NAQI" in cpcb["regulatory_disclaimer"]

    # US EPA Model Proxy
    epa = data["us_epa_model_proxy"]
    assert epa["index_type"] == "US_EPA_BREAKPOINT_BASED_MODEL_PROXY"

    # WHO Benchmark
    who = data["who_guideline_benchmark"]
    assert len(who) > 0
    assert who[0]["comparison_status"] == "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"


def test_get_current_aqi_coordinate_validation(client):
    """Out-of-range coordinates must return HTTP 422 Unprocessable Entity."""
    response = client.get("/api/v1/aqi/current?lat=95.0&lon=77.2090")
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "ValidationError"


def test_get_forecast_aqi_success(client):
    """Verify forecast integration returns 24 hours of predictions with valid UTC and offset timestamps."""
    response = client.get("/api/v1/aqi/forecast?lat=28.6139&lon=77.2090")
    assert response.status_code == 200
    data = response.json()

    prov = data["provenance"]
    assert prov["data_provenance"] == "MODEL_FORECAST"
    assert prov["model_cycle_utc"] is None

    series = data["forecast_series"]
    assert len(series) == 24
    assert series[0]["time_utc"].endswith("Z")
    assert "+05:30" in series[0]["time_local"]
    assert series[0]["cpcb_proxy_index"] == 200


def test_indoor_screening_post_endpoint(client):
    payload = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "room_area_sqm": 25.0,
        "ceiling_height_m": 2.6,
        "purifier_cadr_m3h": 250.0,
    }
    response = client.post("/api/v1/indoor/screening", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["outdoor_ambient_pm2_5"] == 90.0
    scenarios = data["scenario_based_heuristic_estimates"]
    assert scenarios["indoor_data_type"] == "UNVERIFIED_ESTIMATE"
    assert abs(scenarios["favorable_envelope_scenario_ug_m3"] - 2.43) < 0.05
    assert abs(scenarios["unfavorable_envelope_scenario_ug_m3"] - 15.96) < 0.05

    purifier = data["purifier_engineering_estimate"]
    assert abs(purifier["equivalent_ach"] - 3.85) < 0.05
    assert "does not constitute or imply official AHAM Verifide certification" in purifier["engineering_context"]


def test_indoor_screening_get_endpoint(client):
    response = client.get("/api/v1/indoor/screening?lat=28.6139&lon=77.2090&room_area_sqm=25.0&ceiling_height_m=2.6&purifier_cadr_m3h=250.0")
    assert response.status_code == 200
    data = response.json()
    assert data["outdoor_ambient_pm2_5"] == 90.0
    assert data["purifier_engineering_estimate"]["equivalent_ach"] == 3.85


def test_upstream_failure_handling(client):
    """When upstream fails, API must return HTTP 503 with zero synthetic data."""
    _CACHE.clear()

    def mock_503(request: httpx.Request):
        return httpx.Response(503, json={"error": "Service unavailable"})

    open_meteo_service._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_503))

    response = client.get("/api/v1/aqi/current?lat=28.6139&lon=77.2090")
    assert response.status_code == 503
    data = response.json()
    assert data["error_type"] == "UpstreamServiceUnavailable"
    assert "No synthetic data generated" in data["detail"]
