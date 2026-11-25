"""WHO 2021 Guideline Benchmark Comparison Service.

Reference:
- World Health Organization (WHO) Global Air Quality Guidelines (2021).
- Distinct Scientific Function:
  WHO guidelines are health-based exposure benchmarks, not an AQI scale.
  Comparing an hourly model estimate against a 24-hour guideline provides indicative
  screening information and does NOT establish 24-hour regulatory non-compliance.
"""

from typing import Any, Dict, List, Optional

WHO_24H_BENCHMARKS: Dict[str, float] = {
    "pm2_5": 15.0,   # µg/m³
    "pm10": 45.0,    # µg/m³
    "no2": 25.0,     # µg/m³
    "so2": 40.0,     # µg/m³
    "co": 4.0,       # mg/m³
    "o3": 100.0,     # µg/m³ (8-hour peak season reference)
}

BENCHMARK_DISCLAIMER = (
    "Compares an instantaneous hourly model estimate against the WHO 2021 24-hour guideline reference level. "
    "It does not establish 24-hour regulatory non-compliance, which requires a verified 24-hour mean concentration."
)


def evaluate_who_benchmarks(
    pollutants: Dict[str, Optional[float]],
) -> List[Dict[str, Any]]:
    """Evaluate hourly model concentrations against WHO 2021 24-hour guideline benchmark levels."""
    evaluations: List[Dict[str, Any]] = []

    for pollutant, benchmark in WHO_24H_BENCHMARKS.items():
        val = pollutants.get(pollutant)
        if val is not None and val >= 0:
            ratio = round(val / benchmark, 2)
            exceeds = val > benchmark
            status = (
                "HOURLY_VALUE_EXCEEDS_24H_BENCHMARK_LEVEL"
                if exceeds
                else "HOURLY_VALUE_WITHIN_24H_BENCHMARK_LEVEL"
            )

            evaluations.append({
                "pollutant": pollutant,
                "hourly_model_concentration": round(val, 2),
                "guideline_24h_benchmark_level": benchmark,
                "ratio_to_24h_benchmark": ratio,
                "comparison_status": status,
                "benchmark_disclaimer": BENCHMARK_DISCLAIMER,
            })

    return evaluations
