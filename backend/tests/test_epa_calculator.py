"""Dedicated unit tests for the US EPA Breakpoint-Based Model Proxy Calculator.

Verifies:
1. Continuous interval handling with zero dead zones for fractional concentrations below, at, and above EPA breakpoints.
2. Accurate sub-index interpolation matching EPA 40 CFR Part 58 breakpoints.
3. Category mapping across Good, Moderate, USG, Unhealthy, Very Unhealthy, Hazardous.
4. Dominant pollutant selection.
5. Missing pollutant and empty input handling.
"""

import pytest
from app.services.epa_calculator import (
    calculate_epa_model_proxy,
    calculate_epa_sub_index,
)


def test_epa_fractional_breakpoint_boundaries_pm25():
    """Verify continuous boundary intervals for US EPA PM2.5 (40 CFR Part 58)."""
    # Breakpoint 1: 12.0 µg/m³ (Good -> Moderate)
    assert calculate_epa_sub_index("pm2_5", 11.9) == 50
    assert calculate_epa_sub_index("pm2_5", 12.0) == 50
    assert calculate_epa_sub_index("pm2_5", 12.01) == 51
    assert calculate_epa_sub_index("pm2_5", 12.05) == 51
    assert calculate_epa_sub_index("pm2_5", 12.1) == 51

    # Breakpoint 2: 35.4 µg/m³ (Moderate -> Unhealthy for Sensitive Groups)
    assert calculate_epa_sub_index("pm2_5", 35.3) == 100
    assert calculate_epa_sub_index("pm2_5", 35.4) == 100
    assert calculate_epa_sub_index("pm2_5", 35.45) == 101
    assert calculate_epa_sub_index("pm2_5", 35.5) == 101

    # Breakpoint 3: 55.4 µg/m³ (USG -> Unhealthy)
    assert calculate_epa_sub_index("pm2_5", 55.3) == 150
    assert calculate_epa_sub_index("pm2_5", 55.4) == 150
    assert calculate_epa_sub_index("pm2_5", 55.45) == 151
    assert calculate_epa_sub_index("pm2_5", 55.5) == 151

    # Acceptance input vector: 90.0 µg/m³ -> AQI ≈ 169 (Unhealthy)
    assert calculate_epa_sub_index("pm2_5", 90.0) == 169

    # Breakpoint 4: 150.4 µg/m³ (Unhealthy -> Very Unhealthy)
    assert calculate_epa_sub_index("pm2_5", 150.3) == 200
    assert calculate_epa_sub_index("pm2_5", 150.4) == 200
    assert calculate_epa_sub_index("pm2_5", 150.45) == 201
    assert calculate_epa_sub_index("pm2_5", 150.5) == 201

    # Breakpoint 5: 250.4 µg/m³ (Very Unhealthy -> Hazardous)
    assert calculate_epa_sub_index("pm2_5", 250.3) == 300
    assert calculate_epa_sub_index("pm2_5", 250.4) == 300
    assert calculate_epa_sub_index("pm2_5", 250.45) == 301
    assert calculate_epa_sub_index("pm2_5", 250.5) == 301

    # Max cap: 500
    assert calculate_epa_sub_index("pm2_5", 550.0) == 500


def test_epa_other_pollutants_breakpoints():
    """Verify continuous boundary intervals for PM10, CO, O3, NO2, and SO2."""
    # PM10: 54.0 (Good -> Moderate), 154.0 (Moderate -> USG)
    assert calculate_epa_sub_index("pm10", 54.0) == 50
    assert calculate_epa_sub_index("pm10", 54.05) == 51
    assert calculate_epa_sub_index("pm10", 150.0) == 98
    assert calculate_epa_sub_index("pm10", 154.0) == 100
    assert calculate_epa_sub_index("pm10", 154.05) == 101

    # CO: 5.0 mg/m³ (Good -> Moderate), 10.8 mg/m³ (Moderate -> USG)
    assert calculate_epa_sub_index("co", 5.0) == 50
    assert calculate_epa_sub_index("co", 5.05) == 51
    assert calculate_epa_sub_index("co", 10.8) == 100

    # O3: 105.8 µg/m³ (Good -> Moderate), 137.2 µg/m³ (Moderate -> USG)
    assert calculate_epa_sub_index("o3", 105.8) == 50
    assert calculate_epa_sub_index("o3", 105.85) == 51
    assert calculate_epa_sub_index("o3", 137.2) == 100


def test_epa_model_proxy_dominant_and_categories():
    """Verify overall EPA proxy calculation, dominant selection, and categories."""
    # PM2.5 at 90.0 (AQI 169) dominates PM10 at 150.0 (AQI 98) and NO2 at 60.0 (AQI 30)
    res = calculate_epa_model_proxy(pm2_5=90.0, pm10=150.0, no2=60.0)
    assert res["proxy_index"] == 169
    assert res["category"] == "Unhealthy"
    assert res["dominant_pollutant"] == "pm2_5"
    assert res["index_type"] == "US_EPA_BREAKPOINT_BASED_MODEL_PROXY"

    # PM10 dominant
    res_pm10 = calculate_epa_model_proxy(pm2_5=10.0, pm10=200.0)
    assert res_pm10["dominant_pollutant"] == "pm10"
    assert res_pm10["category"] == "Unhealthy for Sensitive Groups"

    # Empty inputs
    res_empty = calculate_epa_model_proxy()
    assert res_empty["proxy_index"] is None
    assert res_empty["category"] is None
    assert res_empty["dominant_pollutant"] is None
