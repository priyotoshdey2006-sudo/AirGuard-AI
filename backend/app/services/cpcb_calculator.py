"""CPCB Breakpoint-Based Model Proxy Calculation Service.

Reference:
- Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change, Govt. of India:
  "National Air Quality Index" (October 2014 report).
- Regulatory Requirement:
  Statutory CPCB NAQI requires continuous ground monitoring stations (CAAQMS) with at least 16 hours
  of valid monitoring data within a 24-hour period for 24-hr averaging pollutants (PM10, PM2.5, NO2, SO2, NH3, Pb).
- Point-in-Time Model Proxy:
  This service evaluates an instantaneous model proxy by applying official CPCB breakpoint formulas to
  atmospheric reanalysis/forecast data. It does not claim 24-hour regulatory CAAQMS equivalence.
"""

from typing import Any, Dict, Optional, Tuple


# Sub-index categories and ranges (I_LO, I_HI)
AQI_BANDS = [
    (0, 50, "Good"),
    (51, 100, "Satisfactory"),
    (101, 200, "Moderate"),
    (201, 300, "Poor"),
    (301, 400, "Very Poor"),
    (401, 500, "Severe"),
]

# Continuous Pollutant Breakpoints: (B_LO, B_HI) mapped to each of the 6 AQI bands.
# Interval convention: First band is [B_LO, B_HI]; subsequent bands are (B_LO, B_HI].
# Concentrations in µg/m³, except CO which is in mg/m³.
CPCB_BREAKPOINTS: Dict[str, list[Tuple[float, float]]] = {
    "pm2_5": [
        (0.0, 30.0),
        (30.0, 60.0),
        (60.0, 90.0),
        (90.0, 120.0),
        (120.0, 250.0),
        (250.0, 500.0),
    ],
    "pm10": [
        (0.0, 50.0),
        (50.0, 100.0),
        (100.0, 250.0),
        (250.0, 350.0),
        (350.0, 430.0),
        (430.0, 600.0),
    ],
    "no2": [
        (0.0, 40.0),
        (40.0, 80.0),
        (80.0, 180.0),
        (180.0, 280.0),
        (280.0, 400.0),
        (400.0, 600.0),
    ],
    "so2": [
        (0.0, 40.0),
        (40.0, 80.0),
        (80.0, 380.0),
        (380.0, 800.0),
        (800.0, 1600.0),
        (1600.0, 2000.0),
    ],
    "co": [
        (0.0, 1.0),
        (1.0, 2.0),
        (2.0, 10.0),
        (10.0, 17.0),
        (17.0, 34.0),
        (34.0, 50.0),
    ],
    "o3": [
        (0.0, 50.0),
        (50.0, 100.0),
        (100.0, 168.0),
        (168.0, 208.0),
        (208.0, 748.0),
        (748.0, 1000.0),
    ],
    "nh3": [
        (0.0, 200.0),
        (200.0, 400.0),
        (400.0, 800.0),
        (800.0, 1200.0),
        (1200.0, 1800.0),
        (1800.0, 2500.0),
    ],
    "pb": [
        (0.0, 0.5),
        (0.5, 1.0),
        (1.0, 2.0),
        (2.0, 3.0),
        (3.0, 3.5),
        (3.5, 5.0),
    ],
}

REGULATORY_DISCLAIMER = (
    "This value is a point-in-time model proxy computed by applying CPCB breakpoint formulas "
    "to hourly atmospheric model estimates. It does not represent regulatory CPCB NAQI, which "
    "mandates certified CAAQMS ground monitors with at least 16 hours of valid monitoring data "
    "within a 24-hour period. It cannot be used for statutory compliance or legal purposes."
)


def calculate_cpcb_sub_index(pollutant: str, concentration: float) -> Optional[int]:
    """Calculate the CPCB sub-index for a specific pollutant concentration using continuous intervals.

    Formula: Ip = [(I_HI - I_LO) / (B_HI - B_LO)] * (Cp - B_LO) + I_LO
    """
    if pollutant not in CPCB_BREAKPOINTS or concentration is None or concentration < 0:
        return None

    bands = CPCB_BREAKPOINTS[pollutant]
    for idx, (b_lo, b_hi) in enumerate(bands):
        # Continuous interval: First band is [b_lo, b_hi]; subsequent bands are (b_lo, b_hi]
        is_in_range = (b_lo <= concentration <= b_hi) if idx == 0 else (b_lo < concentration <= b_hi)
        is_above_max = (idx == len(bands) - 1 and concentration > b_hi)

        if is_in_range or is_above_max:
            i_lo, i_hi, _ = AQI_BANDS[idx]
            if is_above_max:
                return 500  # Cap at max severe index per CPCB guidelines

            sub_index = ((i_hi - i_lo) / (b_hi - b_lo)) * (concentration - b_lo) + i_lo
            return int(round(sub_index))

    return None


def get_cpcb_category(aqi_value: int) -> str:
    """Return the official CPCB health category for a calculated index."""
    if aqi_value <= 50:
        return "Good"
    elif aqi_value <= 100:
        return "Satisfactory"
    elif aqi_value <= 200:
        return "Moderate"
    elif aqi_value <= 300:
        return "Poor"
    elif aqi_value <= 400:
        return "Very Poor"
    else:
        return "Severe"


def calculate_cpcb_model_proxy(
    pm2_5: Optional[float] = None,
    pm10: Optional[float] = None,
    no2: Optional[float] = None,
    so2: Optional[float] = None,
    co: Optional[float] = None,
    o3: Optional[float] = None,
    nh3: Optional[float] = None,
    pb: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate the overall CPCB Breakpoint-Based Model Proxy with regulatory completeness checks.

    Minimum Criteria Rule:
    - At least three (3) pollutants must be present.
    - At least one of the present pollutants must be either PM2.5 or PM10.
    - If criteria are not met, returns proxy_index = None and criteria_met = False.
    """
    pollutant_inputs = {
        "pm2_5": pm2_5,
        "pm10": pm10,
        "no2": no2,
        "so2": so2,
        "co": co,
        "o3": o3,
        "nh3": nh3,
        "pb": pb,
    }

    sub_indices: Dict[str, int] = {}
    for pol, conc in pollutant_inputs.items():
        if conc is not None:
            sub = calculate_cpcb_sub_index(pol, conc)
            if sub is not None:
                sub_indices[pol] = sub

    evaluated_count = len(sub_indices)
    has_particulate = ("pm2_5" in sub_indices) or ("pm10" in sub_indices)
    criteria_met = (evaluated_count >= 3) and has_particulate

    if not criteria_met:
        return {
            "proxy_index": None,
            "category": None,
            "dominant_pollutant": None,
            "index_type": "CPCB_BREAKPOINT_BASED_MODEL_PROXY",
            "criteria_met": False,
            "pollutant_count_evaluated": evaluated_count,
            "sub_indices": sub_indices,
            "regulatory_disclaimer": REGULATORY_DISCLAIMER,
            "criteria_explanation": (
                "Insufficient pollutant parameters to satisfy CPCB NAQI calculation criteria. "
                "CPCB requires a minimum of 3 valid pollutants, at least one of which must be PM2.5 or PM10."
            ),
        }

    # Dominant pollutant is the one with the maximum sub-index
    max_pollutant = max(sub_indices, key=sub_indices.get)
    overall_aqi = sub_indices[max_pollutant]
    category = get_cpcb_category(overall_aqi)

    return {
        "proxy_index": overall_aqi,
        "category": category,
        "dominant_pollutant": max_pollutant,
        "index_type": "CPCB_BREAKPOINT_BASED_MODEL_PROXY",
        "criteria_met": True,
        "pollutant_count_evaluated": evaluated_count,
        "sub_indices": sub_indices,
        "regulatory_disclaimer": REGULATORY_DISCLAIMER,
        "criteria_explanation": "CPCB criteria met (>= 3 pollutants including particulate matter).",
    }
