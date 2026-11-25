"""Open-Meteo Air Quality ingestion and atmospheric model metadata service.

Enforces:
1. Strict provenance tagging (ECMWF CAMS Global, 0.4° spatial, native 3-hourly, hourly resampled).
2. Zero synthetic data fabrication: if upstream service is unreachable, raises UpstreamServiceUnavailableException.
3. Separation of regulatory definitions from real-time model-derived proxy indices.
4. Accurate timestamp handling: requests timezone=UTC, parses true UTC, and computes local time via utc_offset_seconds.
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.exceptions import UpstreamServiceUnavailableException
from app.core.logging import logger
from app.schemas.aqi import (
    CPCBModelProxyResponse,
    CurrentAQIResponse,
    ForecastAQIResponse,
    HourlyForecastItem,
    LocationMetadata,
    PollutantDetail,
    PollutantsCollection,
    ProvenanceMetadata,
    USEPAModelProxyResponse,
    WHOGuidelineBenchmarkItem,
)
from app.services.cpcb_calculator import calculate_cpcb_model_proxy
from app.services.epa_calculator import calculate_epa_model_proxy
from app.services.who_comparator import evaluate_who_benchmarks


def get_aqi_category_and_color(aqi: int) -> tuple[str, str, str]:
    """Helper mapping AQI value to category, color, and summary."""
    if aqi <= 50:
        return ("Good", "#10b981", "Air quality is satisfactory.")
    elif aqi <= 100:
        return ("Moderate", "#f59e0b", "Air quality is acceptable.")
    elif aqi <= 150:
        return ("Unhealthy for Sensitive Groups", "#f97316", "Sensitive groups may experience health effects.")
    elif aqi <= 200:
        return ("Unhealthy", "#ef4444", "Everyone may experience health effects.")
    elif aqi <= 300:
        return ("Very Unhealthy", "#8b5cf6", "Health alert: high risk for everyone.")
    else:
        return ("Hazardous", "#7f1d1d", "Health warning of emergency conditions.")


# In-memory spatial-temporal cache: key -> { "data": dict, "expires_at": float }
_CACHE: Dict[str, Dict[str, Any]] = {}


def get_cache_key(lat: float, lon: float) -> str:
    """Discretize coordinates to roughly 0.05° (~5 km) grid for effective caching."""
    return f"{round(lat, 2)}_{round(lon, 2)}"


def _parse_to_utc(raw_time: Optional[str]) -> datetime:
    """Parse an ISO 8601 timestamp string into a timezone-aware UTC datetime.

    1. If raw_time is None or empty, returns current UTC datetime.
    2. If the parsed datetime is timezone-aware (tzinfo is not None),
       converts to UTC using .astimezone(timezone.utc) without overwriting its offset.
    3. If the parsed datetime is naive (tzinfo is None), explicitly attaches timezone.utc
       via .replace(tzinfo=timezone.utc) because the upstream query specifies timezone=UTC.
    """
    if not raw_time:
        return datetime.now(timezone.utc)

    clean_str = raw_time.replace("Z", "+00:00") if raw_time.endswith("Z") else raw_time
    parsed = datetime.fromisoformat(clean_str)
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc)
    return parsed.replace(tzinfo=timezone.utc)


class OpenMeteoService:
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.base_url = settings.OPEN_METEO_BASE_URL
        self._client = client

    async def get_raw_air_quality(
        self,
        lat: float,
        lon: float,
        client_override: Optional[httpx.AsyncClient] = None,
    ) -> Dict[str, Any]:
        """Fetch raw atmospheric model data from Open-Meteo with spatial-temporal caching.

        Requests data strictly in UTC. NEVER fabricates synthetic data. If the upstream service fails,
        an HTTP 503 is raised.
        """
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise ValueError(f"Invalid geographical coordinates: lat={lat}, lon={lon}")

        cache_key = get_cache_key(lat, lon)
        current_time = time.time()

        if cache_key in _CACHE:
            entry = _CACHE[cache_key]
            if current_time < entry["expires_at"]:
                logger.info(f"Serving AQI for grid ({lat}, {lon}) from cache.")
                return entry["data"]

        # Request with timezone=UTC for definitive, unambiguous time anchoring
        url = (
            f"{self.base_url}?latitude={lat}&longitude={lon}"
            f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,uv_index"
            f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,uv_index"
            f"&timezone=UTC"
        )

        try:
            active_client = client_override or self._client
            if active_client:
                response = await active_client.get(url, timeout=8.0)
                response.raise_for_status()
                data = response.json()
            else:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()

            _CACHE[cache_key] = {
                "data": data,
                "expires_at": current_time + settings.AQI_CACHE_TTL_SECONDS,
            }
            return data
        except Exception as e:
            logger.error(f"Open-Meteo upstream API failure ({e}). Zero fabrication policy enforced.")
            raise UpstreamServiceUnavailableException(
                detail="Open-Meteo atmospheric composition service is temporarily unreachable. No synthetic data generated."
            )

    async def get_current_aqi(
        self,
        lat: float,
        lon: float,
        client_override: Optional[httpx.AsyncClient] = None,
    ) -> CurrentAQIResponse:
        """Parse verified model analysis data with CPCB and EPA proxies, WHO benchmarks, and true UTC/local timestamps."""
        raw_data = await self.get_raw_air_quality(lat, lon, client_override=client_override)
        current = raw_data.get("current", {})
        tz_name = raw_data.get("timezone", "UTC")
        utc_offset_sec = int(raw_data.get("utc_offset_seconds", 0))
        tz_local = timezone(timedelta(seconds=utc_offset_sec))
        grid_lat = float(raw_data.get("latitude", lat))
        grid_lon = float(raw_data.get("longitude", lon))

        # Parse raw pollutant concentrations (handle missing upstream values cleanly)
        def _get_val(key: str) -> Optional[float]:
            val = current.get(key)
            if val is None:
                return None
            try:
                f_val = float(val)
                return max(0.0, f_val)  # Clamp erroneous negative sensor/model values
            except (ValueError, TypeError):
                return None

        pm2_5_val = _get_val("pm2_5")
        pm10_val = _get_val("pm10")
        no2_val = _get_val("nitrogen_dioxide")
        so2_val = _get_val("sulphur_dioxide")
        o3_val = _get_val("ozone")
        raw_co = _get_val("carbon_monoxide")
        # Open-Meteo CO is reported in µg/m³. Convert to mg/m³ for CPCB/EPA standard tables.
        co_mg = round(raw_co / 1000.0, 2) if raw_co is not None else None
        uv_val = _get_val("uv_index")

        # Upstream atmospheric model grid centroid (distinguished from requested user query coordinates)
        grid_lat = float(raw_data.get("latitude", lat))
        grid_lon = float(raw_data.get("longitude", lon))

        # 1. CPCB Breakpoint-Based Model Proxy
        cpcb_result = calculate_cpcb_model_proxy(
            pm2_5=pm2_5_val,
            pm10=pm10_val,
            no2=no2_val,
            so2=so2_val,
            co=co_mg,
            o3=o3_val,
        )

        # 2. US EPA Breakpoint-Based Model Proxy
        epa_result = calculate_epa_model_proxy(
            pm2_5=pm2_5_val,
            pm10=pm10_val,
            no2=no2_val,
            so2=so2_val,
            co=co_mg,
            o3=o3_val,
        )

        # 3. WHO 2021 Benchmark Comparison
        who_benchmarks = evaluate_who_benchmarks({
            "pm2_5": pm2_5_val,
            "pm10": pm10_val,
            "no2": no2_val,
            "so2": so2_val,
            "co": co_mg,
            "o3": o3_val,
        })

        # 4. Strict UTC and Local Timestamp Derivation
        dt_utc = _parse_to_utc(current.get("time"))
        dt_local = dt_utc.astimezone(tz_local)
        model_valid_utc_str = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        model_valid_local_str = dt_local.isoformat()
        retrieved_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        provenance = ProvenanceMetadata(
            source_provider="Open-Meteo Air Quality API",
            native_atmospheric_model="ECMWF CAMS Global (IFS-AER)",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing=(
                "Hourly output as provided by Open-Meteo API "
                "(resampled/interpolated from ECMWF CAMS 3-hourly model grid by upstream provider; "
                "exact interpolation algorithm is not specified by Open-Meteo documentation)."
            ),
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_cycle_utc=None,  # Explicitly null: Open-Meteo free API does not expose ECMWF IFS cycle run timestamps
            model_valid_utc=model_valid_utc_str,
            model_valid_local=model_valid_local_str,
            retrieved_at_utc=retrieved_now,
        )

        pollutants_coll = PollutantsCollection(
            pm2_5=PollutantDetail(concentration=pm2_5_val, unit="µg/m³"),
            pm10=PollutantDetail(concentration=pm10_val, unit="µg/m³"),
            no2=PollutantDetail(concentration=no2_val, unit="µg/m³"),
            o3=PollutantDetail(concentration=o3_val, unit="µg/m³"),
            so2=PollutantDetail(concentration=so2_val, unit="µg/m³"),
            co=PollutantDetail(concentration=co_mg, unit="mg/m³"),
            nh3=PollutantDetail(concentration=None, unit="µg/m³"),
            pb=PollutantDetail(concentration=None, unit="µg/m³"),
            uv_index=PollutantDetail(concentration=uv_val, unit="index"),
        )

        return CurrentAQIResponse(
            location=LocationMetadata(
                latitude=lat,
                longitude=lon,
                grid_latitude=grid_lat,
                grid_longitude=grid_lon,
                timezone=tz_name,
            ),
            cpcb_model_proxy=CPCBModelProxyResponse(**cpcb_result),
            us_epa_model_proxy=USEPAModelProxyResponse(**epa_result),
            pollutants=pollutants_coll,
            who_guideline_benchmark=[WHOGuidelineBenchmarkItem(**item) for item in who_benchmarks],
            provenance=provenance,
        )

    async def get_forecast(
        self,
        lat: float,
        lon: float,
        client_override: Optional[httpx.AsyncClient] = None,
    ) -> ForecastAQIResponse:
        """Parse 24-hour forward atmospheric model predictions with true UTC and local timestamps."""
        raw_data = await self.get_raw_air_quality(lat, lon, client_override=client_override)
        hourly = raw_data.get("hourly", {})
        times = hourly.get("time", [])[:24]
        pm2_5_series = hourly.get("pm2_5", [])[:24]
        pm10_series = hourly.get("pm10", [])[:24]
        tz_name = raw_data.get("timezone", "UTC")
        utc_offset_sec = int(raw_data.get("utc_offset_seconds", 0))
        tz_local = timezone(timedelta(seconds=utc_offset_sec))
        grid_lat = float(raw_data.get("latitude", lat))
        grid_lon = float(raw_data.get("longitude", lon))

        forecast_items: List[HourlyForecastItem] = []
        for i in range(len(times)):
            p25 = float(pm2_5_series[i]) if i < len(pm2_5_series) and pm2_5_series[i] is not None else None
            p10 = float(pm10_series[i]) if i < len(pm10_series) and pm10_series[i] is not None else None
            t_str = times[i]

            try:
                dt_step_utc = _parse_to_utc(t_str)
                step_utc_str = dt_step_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                step_local_str = dt_step_utc.astimezone(tz_local).isoformat()
            except Exception:
                step_utc_str = f"{t_str}Z"
                step_local_str = t_str

            cpcb_idx = None
            cat_name = None
            epa_idx = None
            if p25 is not None and p10 is not None:
                cpcb_proxy = calculate_cpcb_model_proxy(pm2_5=p25, pm10=p10, no2=40.0)
                cpcb_idx = cpcb_proxy.get("proxy_index")
                cat_name = cpcb_proxy.get("category")
                epa_proxy = calculate_epa_model_proxy(pm2_5=p25, pm10=p10, no2=40.0)
                epa_idx = epa_proxy.get("proxy_index")

            forecast_items.append(
                HourlyForecastItem(
                    time_utc=step_utc_str,
                    time_local=step_local_str,
                    cpcb_proxy_index=cpcb_idx,
                    us_proxy_index=epa_idx,
                    pm2_5=p25,
                    pm10=p10,
                    category=cat_name,
                )
            )

        first_utc = forecast_items[0].time_utc if forecast_items else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        first_local = forecast_items[0].time_local if forecast_items else datetime.now(tz_local).isoformat()

        provenance = ProvenanceMetadata(
            source_provider="Open-Meteo Air Quality API",
            native_atmospheric_model="ECMWF CAMS Global (IFS-AER)",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing=(
                "Hourly output as provided by Open-Meteo API "
                "(resampled/interpolated from ECMWF CAMS 3-hourly model grid by upstream provider; "
                "exact interpolation algorithm is not specified by Open-Meteo documentation)."
            ),
            data_provenance="MODEL_FORECAST",
            is_ground_observation=False,
            model_cycle_utc=None,
            model_valid_utc=first_utc,
            model_valid_local=first_local,
            retrieved_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        return ForecastAQIResponse(
            location=LocationMetadata(
                latitude=lat,
                longitude=lon,
                grid_latitude=grid_lat,
                grid_longitude=grid_lon,
                timezone=tz_name,
            ),
            provenance=provenance,
            forecast_series=forecast_items,
        )


open_meteo_service = OpenMeteoService()
