"""Dedicated tests for the 24-hour diurnal atmospheric model forecast endpoint.

Verifies:
1. GET /api/v1/aqi/forecast returns 24-hour series.
2. Accurate UTC timestamps formatted with ISO 8601 'Z' suffix.
3. Accurate local timestamps formatted with regional timezone offset.
4. CPCB and EPA model proxy indices and category evaluation per hourly step.
5. Strict CAMS provenance metadata reflecting MODEL_FORECAST with model_cycle_utc=None.
6. Coordinate input validation (HTTP 422).
7. Upstream failure returns HTTP 503 without synthetic data fabrication.
"""

import pytest
import httpx
from starlette.testclient import TestClient
from app.main import app
from app.services.open_meteo import open_meteo_service, _CACHE

MOCK_FORECAST_PAYLOAD = {
    "latitude": 28.625,
    "longitude": 77.25,
    "generationtime_ms": 1.5,
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
        "pm10": [100.0 + h * 5 for h in range(24)],
        "pm2_5": [50.0 + h * 3 for h in range(24)],
        "carbon_monoxide": [800.0] * 24,
        "nitrogen_dioxide": [40.0] * 24,
        "sulphur_dioxide": [10.0] * 24,
        "ozone": [35.0] * 24,
        "uv_index": [2.5] * 24,
    },
}


@pytest.fixture(autouse=True)
def setup_mock_open_meteo():
    _CACHE.clear()

    def mock_handler(request: httpx.Request):
        return httpx.Response(200, json=MOCK_FORECAST_PAYLOAD)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    open_meteo_service._client = mock_client
    yield
    open_meteo_service._client = None
    _CACHE.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_forecast_endpoint_success(client):
    """Verify forecast endpoint returns 24 items with strict UTC and local timestamps."""
    response = client.get("/api/v1/aqi/forecast?lat=28.6139&lon=77.2090")
    assert response.status_code == 200
    data = response.json()

    # Location
    loc = data["location"]
    assert loc["latitude"] == 28.6139
    assert loc["longitude"] == 77.2090
    assert loc["timezone"] == "Asia/Kolkata"

    # Provenance
    prov = data["provenance"]
    assert prov["native_atmospheric_model"] == "ECMWF CAMS Global (IFS-AER)"
    assert prov["native_spatial_resolution"] == "0.4° (~45 km)"
    assert prov["native_temporal_resolution"] == "3-hourly"
    assert prov["data_provenance"] == "MODEL_FORECAST"
    assert prov["is_ground_observation"] is False
    assert prov["model_cycle_utc"] is None
    assert prov["model_valid_utc"].endswith("Z")

    # Forecast series
    series = data["forecast_series"]
    assert len(series) == 24

    for i, step in enumerate(series):
        # 1. True UTC: ends in Z and matches the expected hour
        assert step["time_utc"].endswith("Z")
        assert f"T{i:02d}:00:00Z" in step["time_utc"]

        # 2. Local time: offset matches +05:30 (19800 seconds)
        assert "+05:30" in step["time_local"]

        # 3. Model proxies
        assert step["cpcb_proxy_index"] is not None
        assert step["us_proxy_index"] is not None
        assert step["category"] in [
            "Good",
            "Satisfactory",
            "Moderate",
            "Poor",
            "Very Poor",
            "Severe",
        ]
        assert step["pm2_5"] == 50.0 + i * 3
        assert step["pm10"] == 100.0 + i * 5


def test_forecast_endpoint_invalid_coordinates(client):
    """Coordinates out of range must be rejected with HTTP 422."""
    res = client.get("/api/v1/aqi/forecast?lat=91.0&lon=77.2090")
    assert res.status_code == 422

    res_lon = client.get("/api/v1/aqi/forecast?lat=28.6139&lon=-190.0")
    assert res_lon.status_code == 422


def test_forecast_endpoint_upstream_failure_no_fabrication(client):
    """When upstream fails, forecast returns HTTP 503 without synthetic data."""
    def mock_500(request: httpx.Request):
        return httpx.Response(500, json={"error": "ECMWF gateway down"})

    failing_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_500))
    open_meteo_service._client = failing_client

    res = client.get("/api/v1/aqi/forecast?lat=28.6139&lon=77.2090")
    assert res.status_code == 503
    assert "No synthetic data generated" in res.json()["detail"]
