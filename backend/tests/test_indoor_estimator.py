"""Unit tests for the Indoor Air Quality (IAQ) Screening Mass-Balance Estimator."""

import pytest
from app.services.indoor_estimator import calculate_indoor_screening


def test_indoor_screening_favorable_and_unfavorable_scenarios():
    """Verify exact mathematical derivations with baseline inputs:

    Cout = 90.0 µg/m³, Area = 25.0 m², Height = 2.6 m -> Volume = 65.0 m³, CADR = 250.0 m³/hr.

    Favorable:
      Numerator = 0.40 * 0.30 * 90.0 = 10.8
      CADR/V = 250 / 65 = 3.846154
      Denominator = 0.30 + 0.30 + 3.846154 = 4.446154
      Result = 10.8 / 4.446154 ≈ 2.4291 -> 2.43 µg/m³
      tau = 1 / 4.446154 ≈ 0.2249 hr -> 13.5 min

    Unfavorable:
      Numerator = 0.85 * 0.80 * 90.0 = 61.2
      CADR_eff/V = (0.75 * 250) / 65 = 187.5 / 65 = 2.884615
      Denominator = 0.80 + 0.15 + 2.884615 = 3.834615
      Result = 61.2 / 3.834615 ≈ 15.9599 -> 15.96 µg/m³
      tau = 1 / 3.834615 ≈ 0.2608 hr -> 15.6 min
    """
    res = calculate_indoor_screening(
        outdoor_pm2_5=90.0,
        room_area_sqm=25.0,
        ceiling_height_m=2.6,
        purifier_cadr_m3h=250.0,
    )

    scenarios = res["scenario_based_heuristic_estimates"]
    assert scenarios["indoor_data_type"] == "UNVERIFIED_ESTIMATE"
    assert "statistically validated confidence intervals" in scenarios["disclaimer"]

    # Check concentrations
    assert abs(scenarios["favorable_envelope_scenario_ug_m3"] - 2.43) < 0.02
    assert abs(scenarios["unfavorable_envelope_scenario_ug_m3"] - 15.96) < 0.02

    # Check dynamic response parameters
    dynamics = res["dynamics"]
    fav_dyn = dynamics["favorable_scenario"]
    unfav_dyn = dynamics["unfavorable_scenario"]

    assert abs(fav_dyn["time_constant_tau_minutes"] - 13.5) < 0.2
    assert abs(unfav_dyn["time_constant_tau_minutes"] - 15.6) < 0.2
    assert abs(fav_dyn["effective_clearance_rate_hr"] - 4.446) < 0.02
    assert abs(unfav_dyn["effective_clearance_rate_hr"] - 3.835) < 0.02

    # Check equivalent ACH
    purifier = res["purifier_engineering_estimate"]
    assert abs(purifier["equivalent_ach"] - 3.85) < 0.02
    assert "4.80 ACH" in purifier["engineering_context"]
    assert "does not constitute or imply official AHAM Verifide certification" in purifier["engineering_context"]

    # Check ventilation status
    assert res["ventilation_status"]["status"] == "UNFAVORABLE"


def test_indoor_screening_no_purifier():
    """Verify behavior when CADR = 0 (natural infiltration only)."""
    res = calculate_indoor_screening(
        outdoor_pm2_5=50.0,
        room_area_sqm=20.0,
        ceiling_height_m=2.5,
        purifier_cadr_m3h=0.0,
    )

    scenarios = res["scenario_based_heuristic_estimates"]
    # Without CADR, concentrations are noticeably higher
    assert scenarios["favorable_envelope_scenario_ug_m3"] > 5.0
    assert scenarios["unfavorable_envelope_scenario_ug_m3"] > 25.0

    purifier = res["purifier_engineering_estimate"]
    assert purifier["equivalent_ach"] == 0.0
    assert "No active air purifier CADR" in purifier["engineering_context"]
