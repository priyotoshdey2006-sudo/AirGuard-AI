"""US EPA Breakpoint-Based Model Proxy Calculation Service.

Reference:
- US EPA Air Quality Index (AQI) Breakpoints (40 CFR Part 58, Appendix G).
- Regulatory Requirement:
  Statutory US EPA AQI mandates certified Federal Reference Method (FRM) or Federal Equivalent Method (FEM)
  monitors with specific averaging periods (24-hr block for PM2.5/PM10, 8-hr rolling for O3/CO, 1-hr for NO2/SO2).
- Point-in-Time Model Proxy:
  This service evaluates an instantaneous model proxy by applying EPA AQI breakpoints to hourly atmospheric
  reanalysis/forecast concentrations. It is provided for international comparative reference and does not claim
  statutory EPA regulatory equivalence.
"""

from typing import Any, Dict, Optional, Tuple


EPA_AQI_BANDS = [
    (0, 50, "Good"),
    (51, 100, "Moderate"),
    (101, 150, "Unhealthy for Sensitive Groups"),
    (151, 200, "Unhealthy"),
    (201, 300, "Very Unhealthy"),
    (301, 500, "Hazardous"),
]

# Continuous Breakpoints in standard metric concentration units:
# First interval is [B_LO, B_HI]; subsequent intervals are (B_LO, B_HI].
# PM2.5 (µg/m³), PM10 (µg/m³), CO (mg/m³), O3 (µg/m³), NO2 (µg/m³), SO2 (µg/m³)
EPA_BREAKPOINTS: Dict[str, list[Tuple[float, float]]] = {
    "pm2_5": [
        (0.0, 12.0),
        (12.0, 35.4),
        (35.4, 55.4),
        (55.4, 150.4),
        (150.4, 250.4),
        (250.4, 500.4),
    ],
    "pm10": [
        (0.0, 54.0),
        (54.0, 154.0),
        (154.0, 254.0),
        (254.0, 354.0),
        (354.0, 424.0),
        (424.0, 604.0),
    ],
    # CO converted from ppm (1 ppm ≈ 1.145 mg/m³ at 25°C)
    "co": [
        (0.0, 5.0),
        (5.0, 10.8),
        (10.8, 14.2),
        (14.2, 17.6),
        (17.6, 34.8),
        (34.8, 57.7),
    ],
    # O3 converted from ppm (1 ppm ≈ 1960 µg/m³)
    "o3": [
        (0.0, 105.8),
        (105.8, 137.2),
        (137.2, 166.6),
        (166.6, 205.8),
        (205.8, 392.0),
        (392.0, 980.0),
    ],
    # NO2 converted from ppb (1 ppb ≈ 1.88 µg/m³)
    "no2": [
        (0.0, 99.6),
        (99.6, 188.0),
        (188.0, 676.8),
        (676.8, 1220.1),
        (1220.1, 2348.1),
        (2348.1, 3852.1),
    ],
    # SO2 converted from ppb (1 ppb ≈ 2.62 µg/m³)
    "so2": [
        (0.0, 91.7),
        (91.7, 196.5),
        (196.5, 484.7),
        (484.7, 796.5),
        (796.5, 1582.5),
        (1582.5, 2620.0),
    ],
}

EPA_REGULATORY_DISCLAIMER = (
    "This value is a point-in-time model proxy computed by applying US EPA AQI breakpoints (40 CFR Part 58) "
    "to hourly model estimates. Official regulatory US EPA AQI mandates specific temporal averaging periods "
    "(e.g., 24-hour block averages for PM2.5 and PM10, 8-hour rolling averages for Ozone and CO) collected "
    "from certified FRM/FEM ground monitors. It is provided for international comparative reference only."
)


def calculate_epa_sub_index(pollutant: str, concentration: float) -> Optional[int]:
    """Calculate the US EPA sub-index for a specific pollutant concentration using continuous intervals."""
    if pollutant not in EPA_BREAKPOINTS or concentration is None or concentration < 0:
        return None

    bands = EPA_BREAKPOINTS[pollutant]
    for idx, (b_lo, b_hi) in enumerate(bands):
        # Continuous interval: First band is [b_lo, b_hi]; subsequent bands are (b_lo, b_hi]
        is_in_range = (b_lo <= concentration <= b_hi) if idx == 0 else (b_lo < concentration <= b_hi)
        is_above_max = (idx == len(bands) - 1 and concentration > b_hi)

        if is_in_range or is_above_max:
            i_lo, i_hi, _ = EPA_AQI_BANDS[idx]
            if is_above_max:
                return 500

            sub = ((i_hi - i_lo) / (b_hi - b_lo)) * (concentration - b_lo) + i_lo
            return int(round(sub))

    return None


def calculate_epa_model_proxy(
    pm2_5: Optional[float] = None,
    pm10: Optional[float] = None,
    no2: Optional[float] = None,
    so2: Optional[float] = None,
    co: Optional[float] = None,
    o3: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate US EPA Breakpoint-Based Model Proxy."""
    pollutant_inputs = {
        "pm2_5": pm2_5,
        "pm10": pm10,
        "no2": no2,
        "so2": so2,
        "co": co,
        "o3": o3,
    }

    sub_indices: Dict[str, int] = {}
    for pol, conc in pollutant_inputs.items():
        if conc is not None:
            sub = calculate_epa_sub_index(pol, conc)
            if sub is not None:
                sub_indices[pol] = sub

    if not sub_indices:
        return {
            "proxy_index": None,
            "category": None,
            "dominant_pollutant": None,
            "index_type": "US_EPA_BREAKPOINT_BASED_MODEL_PROXY",
            "regulatory_disclaimer": EPA_REGULATORY_DISCLAIMER,
        }

    max_pollutant = max(sub_indices, key=sub_indices.get)
    overall_aqi = sub_indices[max_pollutant]

    # Category determination
    category = "Good"
    for i_lo, i_hi, cat_name in EPA_AQI_BANDS:
        if i_lo <= overall_aqi <= i_hi:
            category = cat_name
            break
    if overall_aqi > 500:
        category = "Hazardous"

    return {
        "proxy_index": overall_aqi,
        "category": category,
        "dominant_pollutant": max_pollutant,
        "index_type": "US_EPA_BREAKPOINT_BASED_MODEL_PROXY",
        "sub_indices": sub_indices,
        "regulatory_disclaimer": EPA_REGULATORY_DISCLAIMER,
    }
