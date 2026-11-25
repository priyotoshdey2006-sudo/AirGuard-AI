"""Dedicated API tests for geospatial air quality queries and spatial health diagnostics.

Verifies:
1. GET /api/v1/aqi/nearby returns matching grid points within radius.
2. Coordinate validation (HTTP 422) for latitude and longitude outside [-90, 90] and [-180, 180].
3. Radius validation (HTTP 422) for non-positive or excessive search radius.
4. Clean response when no atmospheric model records match within radius (zero fabrication).
5. Explicit distinction between requested query location and model grid centroid.
6. Provenance metadata and spatial disclaimer contracts.
7. /api/v1/health and /api/v1/health/db connectivity and diagnostic probes.
"""

import pytest
import httpx
from starlette.testclient import TestClient
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
    from app.db.session import init_db
    init_db()
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
    with TestClient(app) as client:
        yield client


def test_get_nearby_aqi_success(client):
    """Verify nearby AQI query returns matching grid centroids within specified radius."""
    # 1. Populate spatial database via current endpoint
    ingest_res = client.get("/api/v1/aqi/current?lat=28.6139&lon=77.2090")
    assert ingest_res.status_code == 200

    # 2. Query nearby grids within 50 km
    response = client.get("/api/v1/aqi/nearby?lat=28.6139&lon=77.2090&radius_km=50.0&limit=5")
    assert response.status_code == 200
    data = response.json()

    # Query location vs grid centroid distinction
    query_loc = data["query_location"]
    assert query_loc["query_latitude"] == 28.6139
    assert query_loc["query_longitude"] == 77.2090
    assert query_loc["search_radius_km"] == 50.0

    assert data["total_matching_grids"] >= 1
    item = data["items"][0]

    # Grid centroid coordinates strictly preserve model grid coordinates (28.625, 77.25)
    assert item["grid_latitude"] == 28.625
    assert item["grid_longitude"] == 77.25
    assert item["distance_km"] <= 50.0

    # Provenance and scientific constraints
    assert item["spatial_resolution"] == "0.4° (~45 km)"
    assert "model grid centroid, NOT a physical ground sensor" in item["scientific_notes"]
    assert item["provenance"]["native_atmospheric_model"] == "ECMWF CAMS Global (IFS-AER)"
    assert item["provenance"]["is_ground_observation"] is False
    assert item["provenance"]["model_cycle_utc"] is None

    # Spatial disclaimer
    assert "do not constitute street-level microclimate observations" in data["spatial_disclaimer"]


def test_get_nearby_aqi_coordinate_validation(client):
    """Out-of-range coordinates must return HTTP 422."""
    res_lat = client.get("/api/v1/aqi/nearby?lat=95.0&lon=77.2090")
    assert res_lat.status_code == 422

    res_lon = client.get("/api/v1/aqi/nearby?lat=28.6139&lon=185.0")
    assert res_lon.status_code == 422


def test_get_nearby_aqi_radius_validation(client):
    """Non-positive or excessive search radius must return HTTP 422."""
    res_zero = client.get("/api/v1/aqi/nearby?lat=28.6139&lon=77.2090&radius_km=0.0")
    assert res_zero.status_code == 422

    res_negative = client.get("/api/v1/aqi/nearby?lat=28.6139&lon=77.2090&radius_km=-10.0")
    assert res_negative.status_code == 422

    res_too_large = client.get("/api/v1/aqi/nearby?lat=28.6139&lon=77.2090&radius_km=300.0")
    assert res_too_large.status_code == 422


def test_get_nearby_aqi_empty_result_when_radius_too_tight(client):
    """When no grids exist within an unpopulated region, return clear empty result without fabricating data."""
    # Remote coordinates where no atmospheric model data has been persisted
    res = client.get("/api/v1/aqi/nearby?lat=10.5&lon=10.5&radius_km=1.0")
    assert res.status_code == 200
    data = res.json()
    assert data["total_matching_grids"] == 0
    assert data["items"] == []
    assert "No atmospheric model data available within" in data["message"]


def test_health_check_endpoints(client):
    """Verify /health and /health/db endpoints."""
    # Liveness probe
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "online"
    assert health_data["database"] in ["healthy", "unhealthy"]

    # Database diagnostic probe
    res_db = client.get("/api/v1/health/db")
    assert res_db.status_code == 200
    db_data = res_db.json()
    assert "status" in db_data
    assert "dialect" in db_data["details"]


def test_off_grid_query_persists_model_grid_centroid(client):
    """Verify off-grid query coordinates (28.6139, 77.2090) preserve the upstream grid centroid (28.625, 77.25)."""
    # 1. Fetch current AQI for off-grid coordinate
    res = client.get("/api/v1/aqi/current?lat=28.6139&lon=77.2090")
    assert res.status_code == 200
    data = res.json()

    # Requested user coordinates vs CAMS atmospheric grid centroid
    assert data["location"]["latitude"] == 28.6139
    assert data["location"]["longitude"] == 77.2090
    assert data["location"]["grid_latitude"] == 28.625
    assert data["location"]["grid_longitude"] == 77.25

    # 2. Query nearby endpoint
    nearby_res = client.get("/api/v1/aqi/nearby?lat=28.6139&lon=77.2090&radius_km=20.0")
    assert nearby_res.status_code == 200
    nearby_data = nearby_res.json()

    assert nearby_data["query_location"]["query_latitude"] == 28.6139
    assert nearby_data["query_location"]["query_longitude"] == 77.2090
    assert len(nearby_data["items"]) >= 1

    item = nearby_data["items"][0]
    assert item["grid_latitude"] == 28.625
    assert item["grid_longitude"] == 77.25


@pytest.mark.asyncio
async def test_nearby_aqi_deduplicates_multiple_timestamps_per_grid():
    """Verify nearby AQI returns only the latest record per unique grid point, preventing duplicate grid cells."""
    from datetime import datetime, timezone, timedelta
    import uuid
    import random
    from app.db.session import AsyncSessionLocal
    from app.models.aqi_record import AQIRecord
    from app.services.aqi_persistence import aqi_persistence_service

    base_lat = round(31.0 + random.uniform(0.1, 5.0), 4)
    base_lon = round(74.0 + random.uniform(0.1, 5.0), 4)
    loc_key = f"{base_lat}_{base_lon}_{uuid.uuid4().hex[:6]}"
    t_old = datetime(2026, 11, 21, 10, 0, 0, tzinfo=timezone.utc)
    t_new = datetime(2026, 11, 21, 11, 0, 0, tzinfo=timezone.utc)

    async with AsyncSessionLocal() as session:
        # Insert older record
        rec_old = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=base_lat,
            grid_longitude=base_lon,
            geom=f"POINT({base_lon} {base_lat})",
            pm2_5=40.0,
            pm10=80.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=t_old,
            model_valid_local=t_old.isoformat(),
            retrieved_at_utc=t_old,
            expires_at_utc=t_old + timedelta(hours=1),
        )
        # Insert newer record for SAME grid centroid
        rec_new = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=base_lat,
            grid_longitude=base_lon,
            geom=f"POINT({base_lon} {base_lat})",
            pm2_5=85.0,  # Distinct concentration
            pm10=140.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=t_new,
            model_valid_local=t_new.isoformat(),
            retrieved_at_utc=t_new,
            expires_at_utc=t_new + timedelta(hours=1),
        )
        session.add(rec_old)
        session.add(rec_new)
        await session.commit()

        # Query nearby
        results = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=base_lat,
            longitude=base_lon,
            radius_km=10.0,
            limit=10,
        )

        # Must return exactly ONE record for this grid point
        matching = [r for r, d in results if r.grid_latitude == base_lat and r.grid_longitude == base_lon]
        assert len(matching) == 1
        # Must be the newer timestamp
        assert matching[0].model_valid_utc == t_new
        assert matching[0].pm2_5 == 85.0

        # Clean up
        await session.delete(rec_old)
        await session.delete(rec_new)
        await session.commit()


@pytest.mark.asyncio
async def test_current_vs_future_model_record_selection_policy(client):
    """Verify that current AQI queries select the latest valid current record and NEVER accidentally select future forecasts.
    
    Selection Policy:
    1. Default (include_forecast=False): Only records where model_valid_utc <= target_time_utc are considered.
       The furthest-future forecast timestamp is strictly excluded.
    2. Explicit forecast (include_forecast=True): Future forecasts are included.
    3. Staleness: Records older than AQI_CACHE_TTL_SECONDS are flagged is_stale=True.
    """
    from datetime import datetime, timezone, timedelta
    import uuid
    import random
    from app.db.session import AsyncSessionLocal
    from app.models.aqi_record import AQIRecord

    test_lat = round(26.0 + random.uniform(0.1, 5.0), 4)
    test_lon = round(75.0 + random.uniform(0.1, 5.0), 4)
    loc_key = f"temporal_{test_lat}_{test_lon}_{uuid.uuid4().hex[:6]}"

    now = datetime.now(timezone.utc)
    t_past = now - timedelta(hours=2)       # 2 hours ago (stale)
    t_current = now - timedelta(minutes=5)   # 5 minutes ago (current analysis)
    t_future = now + timedelta(hours=6)     # 6 hours ahead (future forecast)

    async with AsyncSessionLocal() as session:
        # Record 1: Historical analysis (pm2.5 = 35.0)
        rec_past = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=test_lat,
            grid_longitude=test_lon,
            geom=f"POINT({test_lon} {test_lat})",
            pm2_5=35.0,
            pm10=70.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=t_past,
            model_valid_local=t_past.isoformat(),
            retrieved_at_utc=t_past,
            expires_at_utc=t_past + timedelta(hours=1),
        )
        # Record 2: Current analysis (pm2.5 = 70.0)
        rec_current = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=test_lat,
            grid_longitude=test_lon,
            geom=f"POINT({test_lon} {test_lat})",
            pm2_5=70.0,
            pm10=120.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=t_current,
            model_valid_local=t_current.isoformat(),
            retrieved_at_utc=now,
            expires_at_utc=now + timedelta(hours=1),
        )
        # Record 3: Future diurnal forecast (pm2.5 = 150.0)
        rec_future = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=test_lat,
            grid_longitude=test_lon,
            geom=f"POINT({test_lon} {test_lat})",
            pm2_5=150.0,
            pm10=250.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_FORECAST",
            is_ground_observation=False,
            model_valid_utc=t_future,
            model_valid_local=t_future.isoformat(),
            retrieved_at_utc=now,
            expires_at_utc=now + timedelta(hours=1),
        )
        session.add(rec_past)
        session.add(rec_current)
        session.add(rec_future)
        await session.commit()

    # 1. Default Query (include_forecast=False): MUST select current (70.0), NOT future (150.0)
    res_default = client.get(f"/api/v1/aqi/nearby?lat={test_lat}&lon={test_lon}&radius_km=10.0")
    assert res_default.status_code == 200
    data_default = res_default.json()
    matching_default = [item for item in data_default["items"] if item["grid_latitude"] == test_lat and item["grid_longitude"] == test_lon]
    assert len(matching_default) == 1
    selected = matching_default[0]
    assert selected["pollutants"]["pm2_5"]["concentration"] == 70.0, "Must select current observation, not future forecast"
    assert selected["is_stale"] is False

    # 2. Forecast Query (include_forecast=True): MUST select the furthest forecast (150.0)
    res_forecast = client.get(f"/api/v1/aqi/nearby?lat={test_lat}&lon={test_lon}&radius_km=10.0&include_forecast=true")
    assert res_forecast.status_code == 200
    data_forecast = res_forecast.json()
    matching_forecast = [item for item in data_forecast["items"] if item["grid_latitude"] == test_lat and item["grid_longitude"] == test_lon]
    assert len(matching_forecast) == 1
    assert matching_forecast[0]["pollutants"]["pm2_5"]["concentration"] == 150.0

    # 3. Historical Target Time (target_time_utc set to 90 min ago): MUST select rec_past (35.0)
    t_target = (now - timedelta(minutes=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    res_hist = client.get(f"/api/v1/aqi/nearby?lat={test_lat}&lon={test_lon}&radius_km=10.0&target_time_utc={t_target}")
    assert res_hist.status_code == 200
    data_hist = res_hist.json()
    matching_hist = [item for item in data_hist["items"] if item["grid_latitude"] == test_lat and item["grid_longitude"] == test_lon]
    assert len(matching_hist) == 1
    assert matching_hist[0]["pollutants"]["pm2_5"]["concentration"] == 35.0

    # Clean up records
    async with AsyncSessionLocal() as session:
        for r_id in [rec_past.id, rec_current.id, rec_future.id]:
            obj = await session.get(AQIRecord, r_id)
            if obj:
                await session.delete(obj)
        await session.commit()

