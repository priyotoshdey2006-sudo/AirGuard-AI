"""Tests for Open-Meteo ingestion, CAMS provenance metadata, strict timestamp handling, and zero-fabrication error handling."""

from datetime import datetime, timezone, timedelta
import pytest
import httpx
from app.core.exceptions import UpstreamServiceUnavailableException
from app.services.open_meteo import OpenMeteoService, _CACHE, _parse_to_utc


MOCK_OPEN_METEO_JSON = {
    "latitude": 28.625,
    "longitude": 77.25,
    "generationtime_ms": 1.25,
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


@pytest.mark.asyncio
async def test_open_meteo_successful_parsing_and_provenance():
    """Verify that verified model analysis parsing preserves CAMS provenance,

    executes CPCB model proxy, and flags WHO benchmark comparison without claiming 24h compliance.
    """
    _CACHE.clear()

    captured_urls = []

    def mock_handler(request: httpx.Request):
        captured_urls.append(str(request.url))
        return httpx.Response(200, json=MOCK_OPEN_METEO_JSON)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    service = OpenMeteoService(client=mock_client)

    res = await service.get_current_aqi(lat=28.6139, lon=77.2090)

    # 0. Request URL contains timezone=UTC
    assert any("timezone=UTC" in u for u in captured_urls)

    # 1. Provenance Verification
    prov = res.provenance
    assert prov.native_atmospheric_model == "ECMWF CAMS Global (IFS-AER)"
    assert prov.native_spatial_resolution == "0.4° (~45 km)"
    assert prov.native_temporal_resolution == "3-hourly"
    assert "Hourly output as provided by Open-Meteo API" in prov.temporal_processing
    assert prov.is_ground_observation is False
    assert prov.model_cycle_utc is None
    assert prov.data_provenance == "MODEL_ANALYSIS"

    # 2. Strict Timestamps: UTC ends in Z, local preserves offset +05:30
    assert prov.model_valid_utc == "2026-11-21T10:00:00Z"
    assert prov.model_valid_local.startswith("2026-11-21T15:30:00+05:30")
    assert not prov.model_valid_local.endswith("Z")
    assert prov.retrieved_at_utc.endswith("Z")

    # 3. CPCB Model Proxy Verification (90.0 PM2.5, 150.0 PM10, 60.0 NO2 -> 200 Moderate)
    cpcb = res.cpcb_model_proxy
    assert cpcb.proxy_index == 200
    assert cpcb.category == "Moderate"
    assert cpcb.dominant_pollutant == "pm2_5"
    assert cpcb.index_type == "CPCB_BREAKPOINT_BASED_MODEL_PROXY"
    assert "regulatory CPCB NAQI" in cpcb.regulatory_disclaimer

    # 4. US EPA Model Proxy Verification
    epa = res.us_epa_model_proxy
    assert epa.index_type == "US_EPA_BREAKPOINT_BASED_MODEL_PROXY"
    assert epa.proxy_index is not None

    # 5. WHO Guideline Benchmark Verification
    who = res.who_guideline_benchmark
    pm25_who = next((w for w in who if w.pollutant == "pm2_5"), None)
    assert pm25_who is not None
    assert pm25_who.guideline_24h_benchmark_level == 15.0
    assert pm25_who.ratio_to_24h_benchmark == 6.0
    assert pm25_who.comparison_status == "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"
    assert "does not establish 24-hour regulatory non-compliance" in pm25_who.benchmark_disclaimer


@pytest.mark.asyncio
async def test_open_meteo_timestamp_offsets_and_missing_fields():
    """Verify timezone offset handling, missing timestamp fallback, and null pollutant tolerance."""
    _CACHE.clear()

    payload_with_missing = {
        "latitude": 51.5,
        "longitude": -0.12,
        "utc_offset_seconds": 0,
        "timezone": "UTC",
        "current": {
            # time omitted to verify fallback
            "pm10": None,
            "pm2_5": None,
            "carbon_monoxide": None,
            "nitrogen_dioxide": None,
            "sulphur_dioxide": None,
            "ozone": None,
            "uv_index": None,
        },
        "hourly": {
            "time": ["2026-11-21T00:00"],
            "pm10": [None],
            "pm2_5": [None],
        },
    }

    def mock_handler(request: httpx.Request):
        return httpx.Response(200, json=payload_with_missing)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    service = OpenMeteoService(client=mock_client)

    res = await service.get_current_aqi(lat=51.5, lon=-0.12)

    # Missing model timestamp falls back to UTC now with 'Z' suffix
    assert res.provenance.model_valid_utc.endswith("Z")
    assert res.provenance.model_cycle_utc is None  # Never fabricated

    # Null pollutants produce None proxy index without raising exceptions
    assert res.cpcb_model_proxy.proxy_index is None
    assert res.us_epa_model_proxy.proxy_index is None
    assert res.pollutants.pm2_5.concentration is None
    assert res.pollutants.pm10.concentration is None


@pytest.mark.asyncio
async def test_open_meteo_negative_concentration_clamping():
    """Erroneous negative atmospheric model values must be clamped to 0.0."""
    _CACHE.clear()

    payload_with_negative = {
        "latitude": 28.625,
        "longitude": 77.25,
        "utc_offset_seconds": 0,
        "timezone": "UTC",
        "current": {
            "time": "2026-11-21T12:00",
            "pm10": -5.0,
            "pm2_5": 20.0,
            "carbon_monoxide": -100.0,
        },
        "hourly": {
            "time": ["2026-11-21T12:00"],
            "pm10": [-5.0],
            "pm2_5": [20.0],
        },
    }

    def mock_handler(request: httpx.Request):
        return httpx.Response(200, json=payload_with_negative)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    service = OpenMeteoService(client=mock_client)

    res = await service.get_current_aqi(lat=28.625, lon=77.25)
    assert res.pollutants.pm10.concentration == 0.0
    assert res.pollutants.pm2_5.concentration == 20.0
    assert res.pollutants.co.concentration == 0.0


@pytest.mark.asyncio
async def test_open_meteo_upstream_failure_zero_fabrication():
    """Verify that when Open-Meteo fails (HTTP 500 or timeout),

    the service raises UpstreamServiceUnavailableException and NEVER fabricates synthetic data.
    """
    _CACHE.clear()

    def mock_failure_handler(request: httpx.Request):
        return httpx.Response(500, json={"error": "Internal server error"})

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_failure_handler))
    service = OpenMeteoService(client=mock_client)

    with pytest.raises(UpstreamServiceUnavailableException) as exc_info:
        await service.get_current_aqi(lat=28.6139, lon=77.2090)

    assert exc_info.value.status_code == 503
    assert "No synthetic data generated" in exc_info.value.detail


@pytest.mark.asyncio
async def test_open_meteo_coordinate_validation():
    """Invalid coordinates must raise a ValueError immediately."""
    service = OpenMeteoService()
    with pytest.raises(ValueError):
        await service.get_raw_air_quality(lat=95.0, lon=77.2090)


def test_open_meteo_parse_to_utc_helper():
    """Verify robust timestamp parsing distinguishing naive and timezone-aware inputs.

    - Aware timestamps must use .astimezone(timezone.utc) without overwriting offset.
    - Naive timestamps must use .replace(tzinfo=timezone.utc).
    """
    # 1. Naive string from Open-Meteo UTC
    dt_naive = _parse_to_utc("2026-11-21T10:00")
    assert dt_naive.tzinfo == timezone.utc
    assert dt_naive.strftime("%Y-%m-%dT%H:%M:%SZ") == "2026-11-21T10:00:00Z"

    # 2. Timezone-aware with 'Z' suffix
    dt_z = _parse_to_utc("2026-11-21T10:00:00Z")
    assert dt_z.tzinfo == timezone.utc
    assert dt_z.strftime("%Y-%m-%dT%H:%M:%SZ") == "2026-11-21T10:00:00Z"

    # 3. Timezone-aware with regional offset (+05:30)
    # Must convert 15:30 IST to 10:00 UTC using astimezone, never overwriting offset
    dt_aware = _parse_to_utc("2026-11-21T15:30:00+05:30")
    assert dt_aware.tzinfo == timezone.utc
    assert dt_aware.hour == 10
    assert dt_aware.minute == 0
    assert dt_aware.strftime("%Y-%m-%dT%H:%M:%SZ") == "2026-11-21T10:00:00Z"

    # 4. Empty/None fallback
    dt_none = _parse_to_utc(None)
    assert dt_none.tzinfo == timezone.utc

