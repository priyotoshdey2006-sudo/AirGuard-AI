"""Unit tests for the CPCB Breakpoint-Based Model Proxy Calculator.

Verifies:
1. Exact acceptance vector (90.0, 150.0, 60.0 -> 200, Moderate, pm2_5).
2. Interior test vector (75.0, 120.0, 50.0 -> 149-150).
3. Continuous interval handling with zero dead zones for fractional concentrations below, at, and above every breakpoint.
4. Minimum data criteria enforcement (>= 3 pollutants including particulate matter).
5. Category mappings across all 6 CPCB categories.
"""

import pytest
from app.services.cpcb_calculator import (
    calculate_cpcb_model_proxy,
    calculate_cpcb_sub_index,
    get_cpcb_category,
)


def test_cpcb_model_proxy_exact_acceptance_vector():
    """Given PM2.5 = 90.0, PM10 = 150.0, and NO2 = 60.0:

    Overall index must be 200, category strictly 'Moderate', dominant pollutant 'pm2_5'.
    """
    res = calculate_cpcb_model_proxy(pm2_5=90.0, pm10=150.0, no2=60.0)

    assert res["proxy_index"] == 200
    assert res["category"] == "Moderate"
    assert res["dominant_pollutant"] == "pm2_5"
    assert res["index_type"] == "CPCB_BREAKPOINT_BASED_MODEL_PROXY"
    assert res["criteria_met"] is True
    assert res["pollutant_count_evaluated"] == 3
    assert res["sub_indices"]["pm2_5"] == 200
    assert res["sub_indices"]["pm10"] in [133, 134]
    assert res["sub_indices"]["no2"] in [75, 76]
    assert "regulatory CPCB NAQI" in res["regulatory_disclaimer"]


def test_cpcb_model_proxy_interior_vector():
    """Given PM2.5 = 75.0, PM10 = 120.0, and NO2 = 50.0 (non-boundary interior test vector)."""
    res = calculate_cpcb_model_proxy(pm2_5=75.0, pm10=120.0, no2=50.0)

    assert res["proxy_index"] in [149, 150]
    assert res["category"] == "Moderate"
    assert res["dominant_pollutant"] == "pm2_5"
    assert res["criteria_met"] is True


def test_cpcb_fractional_breakpoint_boundaries_pm25():
    """Verify continuous boundary intervals for PM2.5 with fractional values below, at, and above breakpoints."""
    # Breakpoint 1: 30.0 (Good -> Satisfactory)
    assert calculate_cpcb_sub_index("pm2_5", 29.9) == 50
    assert calculate_cpcb_sub_index("pm2_5", 30.0) == 50
    assert calculate_cpcb_sub_index("pm2_5", 30.05) == 51
    assert calculate_cpcb_sub_index("pm2_5", 30.5) == 52
    assert calculate_cpcb_sub_index("pm2_5", 31.0) == 53

    # Breakpoint 2: 60.0 (Satisfactory -> Moderate)
    assert calculate_cpcb_sub_index("pm2_5", 59.9) == 100
    assert calculate_cpcb_sub_index("pm2_5", 60.0) == 100
    assert calculate_cpcb_sub_index("pm2_5", 60.05) == 101
    assert calculate_cpcb_sub_index("pm2_5", 60.5) == 103

    # Breakpoint 3: 90.0 (Moderate -> Poor)
    assert calculate_cpcb_sub_index("pm2_5", 89.9) == 200
    assert calculate_cpcb_sub_index("pm2_5", 90.0) == 200
    assert calculate_cpcb_sub_index("pm2_5", 90.05) == 201
    assert calculate_cpcb_sub_index("pm2_5", 90.5) == 203

    # Breakpoint 4: 120.0 (Poor -> Very Poor)
    assert calculate_cpcb_sub_index("pm2_5", 119.9) == 300
    assert calculate_cpcb_sub_index("pm2_5", 120.0) == 300
    assert calculate_cpcb_sub_index("pm2_5", 120.05) == 301
    assert calculate_cpcb_sub_index("pm2_5", 120.5) == 301

    # Breakpoint 5: 250.0 (Very Poor -> Severe)
    assert calculate_cpcb_sub_index("pm2_5", 249.9) == 400
    assert calculate_cpcb_sub_index("pm2_5", 250.0) == 400
    assert calculate_cpcb_sub_index("pm2_5", 250.05) == 401
    assert calculate_cpcb_sub_index("pm2_5", 250.5) == 401

    # Over max bracket: capped at 500
    assert calculate_cpcb_sub_index("pm2_5", 600.0) == 500


def test_cpcb_fractional_breakpoint_boundaries_other_pollutants():
    """Verify continuous intervals for PM10, NO2, and CO."""
    # PM10: 50.0 (Good -> Satisfactory), 100.0 (Satisfactory -> Moderate)
    assert calculate_cpcb_sub_index("pm10", 50.0) == 50
    assert calculate_cpcb_sub_index("pm10", 50.5) == 51
    assert calculate_cpcb_sub_index("pm10", 100.0) == 100
    assert calculate_cpcb_sub_index("pm10", 100.5) == 101

    # NO2: 40.0 (Good -> Satisfactory), 80.0 (Satisfactory -> Moderate)
    assert calculate_cpcb_sub_index("no2", 40.0) == 50
    assert calculate_cpcb_sub_index("no2", 40.5) == 52
    assert calculate_cpcb_sub_index("no2", 80.0) == 100
    assert calculate_cpcb_sub_index("no2", 80.5) == 101

    # CO: 1.0 (Good -> Satisfactory), 2.0 (Satisfactory -> Moderate)
    assert calculate_cpcb_sub_index("co", 1.0) == 50
    assert calculate_cpcb_sub_index("co", 1.05) == 53
    assert calculate_cpcb_sub_index("co", 2.0) == 100
    assert calculate_cpcb_sub_index("co", 2.05) == 102


def test_cpcb_minimum_pollutants_criteria_enforcement():
    """Requires at least 3 pollutants, including PM2.5 or PM10."""
    # Only 2 pollutants
    res_two = calculate_cpcb_model_proxy(pm2_5=90.0, pm10=150.0)
    assert res_two["proxy_index"] is None
    assert res_two["criteria_met"] is False

    # 3 pollutants, but no particulate fraction
    res_no_pm = calculate_cpcb_model_proxy(no2=60.0, so2=25.0, co=1.2)
    assert res_no_pm["proxy_index"] is None
    assert res_no_pm["criteria_met"] is False

    # 3 pollutants including PM2.5 -> Success
    res_valid = calculate_cpcb_model_proxy(pm2_5=35.0, no2=45.0, so2=15.0)
    assert res_valid["proxy_index"] is not None
    assert res_valid["criteria_met"] is True


def test_cpcb_category_mapping():
    assert get_cpcb_category(50) == "Good"
    assert get_cpcb_category(51) == "Satisfactory"
    assert get_cpcb_category(100) == "Satisfactory"
    assert get_cpcb_category(101) == "Moderate"
    assert get_cpcb_category(200) == "Moderate"
    assert get_cpcb_category(201) == "Poor"
    assert get_cpcb_category(300) == "Poor"
    assert get_cpcb_category(301) == "Very Poor"
    assert get_cpcb_category(400) == "Very Poor"
    assert get_cpcb_category(401) == "Severe"
    assert get_cpcb_category(500) == "Severe"
