# AirGuard AI — REST API Reference Manual

**Base URL:** `http://localhost:8000`  
**API Version:** `v1` (`/api/v1`)  
**Specification Standard:** OpenAPI 3.1.0 / JSON Schema

---

## 1. System & Health Endpoints

### `GET /`
Returns root service operational information.
- **Response (200 OK):**
```json
{
  "project": "AirGuard AI",
  "status": "operational",
  "documentation": "/docs",
  "version": "1.0.0"
}
```

### `GET /health`
Root liveness probe for Docker healthchecks and container orchestrators.
- **Response (200 OK):**
```json
{
  "status": "healthy",
  "project": "AirGuard AI",
  "version": "1.0.0",
  "timestamp": "2026-11-24T16:30:00.000000Z"
}
```

### `GET /api/v1/health`
Service and database connectivity probe.
- **Response (200 OK):**
```json
{
  "status": "online",
  "service": "AirGuard AI Engine",
  "database": "healthy",
  "postgis_enabled": true,
  "timestamp": "2026-11-24T16:30:00.000000Z",
  "version": "2.0.0"
}
```

### `GET /api/v1/health/db`
Deep diagnostic probe detailing database dialect, driver, and PostGIS extension status.
- **Response (200 OK):**
```json
{
  "status": "ready",
  "details": {
    "connected": true,
    "dialect": "postgresql",
    "driver": "asyncpg",
    "postgis_installed": true,
    "postgis_version": "3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1",
    "error": null
  },
  "timestamp": "2026-11-24T16:30:00.000000Z"
}
```

---

## 2. Air Quality Endpoints

### `GET /api/v1/aqi/current`
Retrieves real-time atmospheric model analysis, calculating CPCB NAQI, US EPA AQI, and WHO benchmark ratios.

- **Query Parameters:**
  - `lat` (float, required, -90.0 to 90.0): Query latitude (e.g., `28.6139`)
  - `lon` (float, required, -180.0 to 180.0): Query longitude (e.g., `77.2090`)

- **Response (200 OK):**
```json
{
  "location": {
    "latitude": 28.6139,
    "longitude": 77.209,
    "grid_latitude": 28.625,
    "grid_longitude": 77.25,
    "timezone": "Asia/Kolkata"
  },
  "cpcb_model_proxy": {
    "proxy_index": 200,
    "category": "Moderate",
    "dominant_pollutant": "pm2_5",
    "index_type": "CPCB_BREAKPOINT_BASED_MODEL_PROXY",
    "criteria_met": true,
    "pollutant_count_evaluated": 6,
    "sub_indices": {
      "pm2_5": 200,
      "pm10": 133,
      "no2": 75,
      "o3": 42,
      "so2": 15,
      "co": 42
    },
    "regulatory_disclaimer": "This is a model proxy derived from ECMWF CAMS grid data and does not constitute statutory regulatory CPCB NAQI reporting.",
    "criteria_explanation": "Valid CPCB proxy requires >= 3 pollutants with PM2.5 or PM10."
  },
  "us_epa_model_proxy": {
    "proxy_index": 169,
    "category": "Unhealthy",
    "dominant_pollutant": "pm2_5",
    "index_type": "US_EPA_BREAKPOINT_BASED_MODEL_PROXY",
    "sub_indices": {
      "pm2_5": 169,
      "pm10": 98
    },
    "regulatory_disclaimer": "Calculated via US EPA Technical Guidance (EPA-454/B-18-007)."
  },
  "pollutants": {
    "pm2_5": { "concentration": 90.0, "unit": "µg/m³", "averaging_basis": "HOURLY_MODEL_ESTIMATE" },
    "pm10": { "concentration": 150.0, "unit": "µg/m³", "averaging_basis": "HOURLY_MODEL_ESTIMATE" },
    "no2": { "concentration": 60.0, "unit": "µg/m³", "averaging_basis": "HOURLY_MODEL_ESTIMATE" },
    "o3": { "concentration": 42.0, "unit": "µg/m³", "averaging_basis": "HOURLY_MODEL_ESTIMATE" },
    "so2": { "concentration": 12.0, "unit": "µg/m³", "averaging_basis": "HOURLY_MODEL_ESTIMATE" },
    "co": { "concentration": 850.0, "unit": "µg/m³", "averaging_basis": "HOURLY_MODEL_ESTIMATE" },
    "uv_index": { "concentration": 3.2, "unit": "index", "averaging_basis": "HOURLY_MODEL_ESTIMATE" }
  },
  "who_guideline_benchmark": [
    {
      "pollutant": "PM2.5",
      "hourly_model_concentration": 90.0,
      "guideline_24h_benchmark_level": 15.0,
      "ratio_to_24h_benchmark": 6.0,
      "comparison_status": "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL",
      "benchmark_disclaimer": "WHO AQG 2021 sets 24h average benchmark at 15 µg/m³."
    }
  ],
  "provenance": {
    "source_provider": "Open-Meteo Air Quality API",
    "native_atmospheric_model": "ECMWF CAMS Global (IFS-AER)",
    "native_spatial_resolution": "0.4° (~45 km)",
    "native_temporal_resolution": "3-hourly",
    "data_provenance": "MODEL_ANALYSIS",
    "is_ground_observation": false,
    "model_valid_utc": "2026-11-24T10:00:00Z",
    "model_valid_local": "2026-11-24T15:30:00+05:30",
    "retrieved_at_utc": "2026-11-24T16:30:00Z"
  }
}
```

### `GET /api/v1/aqi/forecast`
Retrieves 24-hour diurnal forward model projections.

- **Query Parameters:**
  - `lat` (float, required): Latitude
  - `lon` (float, required): Longitude

- **Response (200 OK):**
```json
{
  "location": { "latitude": 28.6139, "longitude": 77.209, "timezone": "Asia/Kolkata" },
  "provenance": { "data_provenance": "MODEL_FORECAST" },
  "forecast_series": [
    {
      "time_utc": "2026-11-24T10:00:00Z",
      "time_local": "2026-11-24T15:30:00+05:30",
      "cpcb_proxy_index": 200,
      "us_proxy_index": 169,
      "pm2_5": 90.0,
      "pm10": 150.0,
      "category": "Moderate"
    }
  ]
}
```

### `GET /api/v1/aqi/nearby`
PostGIS geospatial radius search on native geography points.

- **Query Parameters:**
  - `lat` (float, required): Latitude
  - `lon` (float, required): Longitude
  - `radius_km` (float, default 50.0, max 250.0): Search radius
  - `limit` (int, default 10, max 50): Result count
  - `include_forecast` (bool, default false): Include forecast records

---

## 3. Indoor Air Quality Screening Endpoints

### `POST /api/v1/indoor/screening`
Single-compartment physical box model screening.

- **Request Body:**
```json
{
  "latitude": 28.6139,
  "longitude": 77.209,
  "room_area_sqm": 25.0,
  "ceiling_height_m": 2.6,
  "purifier_cadr_m3h": 250.0
}
```

- **Response (200 OK):**
```json
{
  "outdoor_ambient_pm2_5": 90.0,
  "room_volume_m3": 65.0,
  "scenario_based_heuristic_estimates": {
    "favorable_envelope_scenario_ug_m3": 2.43,
    "unfavorable_envelope_scenario_ug_m3": 15.96,
    "indoor_data_type": "UNVERIFIED_ESTIMATE"
  },
  "purifier_engineering_estimate": {
    "cadr_m3h": 250.0,
    "equivalent_ach": 3.85,
    "engineering_context": "Provides approx 3.85 Air Changes per Hour for room volume 65.0 m³. This engineering estimate does not constitute or imply official AHAM Verifide certification."
  }
}
```

---

## 4. AI Recommendations & Copilot

### `POST /api/v1/recommendations/daily-routine`
Generates health-customized daily activity windows based on diurnal forecast curve.

- **Request Body:**
```json
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "sensitivity_level": "ASTHMATIC",
  "planned_activities": ["Morning Jog", "Commute to Work", "Evening Walk"]
}
```

- **Response (200 OK):**
```json
{
  "sensitivity_level": "ASTHMATIC",
  "overall_risk_assessment": "Elevated particulate risk during morning inversion peak.",
  "daily_summary": "Schedule outdoor exertion strictly between 12:00 and 16:00.",
  "activity_windows": [
    {
      "activity_name": "Morning Jog",
      "optimal_time": "14:00 - 15:00",
      "expected_aqi": 135,
      "safety_rating": "CAUTION",
      "mask_recommendation": "N95_REQUIRED",
      "mitigation_tips": "Avoid high cardiovascular strain outdoors; consider indoor treadmill with HEPA."
    }
  ],
  "action_items": [
    "Equip certified N95 respirator if stepping outdoors during morning hours",
    "Keep indoor HEPA air purifier active on medium/high speed"
  ],
  "indoor_guidance": "Keep windows closed until 12:00 when boundary layer ventilation rises."
}
```

### `POST /api/v1/assistant/chat`
Conversational AI Environmental Copilot grounded in retrieved environmental measurements.

- **Request Body:**
```json
{
  "message": "Should my asthmatic child go to soccer practice this afternoon?",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "sensitivity": "ASTHMATIC"
}
```

- **Response (200 OK):**
```json
{
  "reply": "Based on current ECMWF atmospheric analysis for your location (PM2.5: 90 µg/m³, Moderate CPCB proxy), outdoor athletic exertion poses respiratory risk for children with asthma...",
  "model_provider": "Gemini-2.0-Flash",
  "timestamp": "2026-11-24T16:30:00Z"
}
```

---

## 5. Sustainable Transport & Community Reporting

### `POST /api/v1/transport/compare-routes`
Calculates modal carbon emissions and inhaled particulate intake scores.

- **Request Body:**
```json
{
  "origin_lat": 28.6315,
  "origin_lon": 77.2167,
  "dest_lat": 28.4950,
  "dest_lon": 77.0895,
  "origin_name": "Connaught Place",
  "dest_name": "Cyber Hub Gurgaon"
}
```

- **Response (200 OK):**
```json
{
  "distance_km": 24.2,
  "origin_name": "Connaught Place",
  "dest_name": "Cyber Hub Gurgaon",
  "cleanest_mode": "METRO",
  "lowest_carbon_mode": "BICYCLE",
  "total_trees_equivalent": 1.9,
  "options": [
    {
      "mode": "METRO",
      "mode_label": "Metro Rail (Electrified)",
      "duration_minutes": 42.0,
      "co2_kg": 0.68,
      "co2_saved_kg": 3.97,
      "aqi_exposure_score": 28.5,
      "exposure_level": "LOW",
      "recommended": true,
      "recommendation_reason": "Air-conditioned cabin with mechanical filtration yields lowest inhaled dose and 85% CO2 savings."
    },
    {
      "mode": "ICE_CAR",
      "mode_label": "Private Petrol/Diesel Car",
      "duration_minutes": 55.0,
      "co2_kg": 4.65,
      "co2_saved_kg": 0.0,
      "aqi_exposure_score": 62.0,
      "exposure_level": "MODERATE",
      "recommended": false,
      "recommendation_reason": "Highest carbon footprint and significant urban congestion contribution."
    }
  ]
}
```

### `GET /api/v1/community/reports`
Lists crowdsourced community hazards within given radius.

### `POST /api/v1/community/reports`
Submits a citizen report (Open Garbage Burning, Industrial Smoke, Construction Dust).

### `POST /api/v1/community/reports/{id}/upvote`
Peer verification upvote confirming active hazard.
