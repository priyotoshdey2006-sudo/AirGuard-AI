"""Dedicated unit tests for the WHO 2021 Guideline Benchmark Comparator.

Verifies:
1. Hourly model concentration ratios against 24-hour WHO reference levels.
2. Status flags: HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL vs. HOURLY_VALUE_WITHIN_24H_BENCHMARK_LEVEL.
3. Accurate evaluation across all 6 reference pollutants (PM2.5, PM10, NO2, SO2, CO, O3).
4. Missing / None pollutant handling.
5. Presence of non-compliance disclaimer.
"""

import pytest
from app.services.who_comparator import evaluate_who_benchmarks, WHO_24H_BENCHMARKS


def test_who_comparator_exceedance_and_within_limits():
    """Verify exceedance (PM2.5 = 90.0 > 15.0) and within-limit (SO2 = 12.0 < 40.0) calculations."""
    pollutants = {
        "pm2_5": 90.0,   # Exceeds: 90 / 15 = 6.0x
        "pm10": 45.0,    # Exactly at benchmark: 45 / 45 = 1.0x -> Within limit
        "no2": 50.0,     # Exceeds: 50 / 25 = 2.0x
        "so2": 12.0,     # Within limit: 12 / 40 = 0.3x
        "co": 2.0,       # Within limit: 2 / 4 = 0.5x
        "o3": 120.0,     # Exceeds: 120 / 100 = 1.2x
    }

    evals = evaluate_who_benchmarks(pollutants)
    eval_map = {e["pollutant"]: e for e in evals}

    # PM2.5
    assert eval_map["pm2_5"]["ratio_to_24h_benchmark"] == 6.0
    assert eval_map["pm2_5"]["comparison_status"] == "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"
    assert "does not establish 24-hour regulatory non-compliance" in eval_map["pm2_5"]["benchmark_disclaimer"]

    # PM10 (at threshold)
    assert eval_map["pm10"]["ratio_to_24h_benchmark"] == 1.0
    assert eval_map["pm10"]["comparison_status"] == "HOURLY_VALUE_WITHIN_24H_BENCHMARK_LEVEL"

    # NO2
    assert eval_map["no2"]["ratio_to_24h_benchmark"] == 2.0
    assert eval_map["no2"]["comparison_status"] == "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"

    # SO2
    assert eval_map["so2"]["ratio_to_24h_benchmark"] == 0.3
    assert eval_map["so2"]["comparison_status"] == "HOURLY_VALUE_WITHIN_24H_BENCHMARK_LEVEL"

    # CO
    assert eval_map["co"]["ratio_to_24h_benchmark"] == 0.5
    assert eval_map["co"]["comparison_status"] == "HOURLY_VALUE_WITHIN_24H_BENCHMARK_LEVEL"

    # O3
    assert eval_map["o3"]["ratio_to_24h_benchmark"] == 1.2
    assert eval_map["o3"]["comparison_status"] == "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"


def test_who_comparator_omits_missing_pollutants():
    """Pollutants that are None or negative should be omitted cleanly."""
    pollutants = {
        "pm2_5": 30.0,
        "pm10": None,
        "no2": None,
        "so2": -5.0,  # Invalid negative
    }

    evals = evaluate_who_benchmarks(pollutants)
    evaluated_keys = [e["pollutant"] for e in evals]
    assert "pm2_5" in evaluated_keys
    assert "pm10" not in evaluated_keys
    assert "no2" not in evaluated_keys
    assert "so2" not in evaluated_keys
