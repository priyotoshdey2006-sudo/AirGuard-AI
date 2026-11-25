"""Indoor Air Quality (IAQ) Screening Mass-Balance Service.

Reference & Methodology:
- Single-zone mass-balance steady-state model without indoor emissions (S = 0).
- Calculates scenario-based heuristic estimates (favorable vs. unfavorable building envelope).
- Dynamically derives the characteristic time constant tau = 1 / lambda_eff from actual input parameters.
- Evaluates equivalent air changes per hour (ACH = CADR / V) as an engineering screening estimate,
  clearly contextualized against AHAM Verifide's 4.80 ACH baseline without claiming certification.
- All estimates are classified strictly as UNVERIFIED_ESTIMATE.
"""

from typing import Any, Dict, Optional

INDOOR_DISCLAIMER = (
    "These values are scenario-based heuristic screening estimates derived from idealized building "
    "envelope assumptions (zero indoor emissions S=0, steady-state mass balance). They are neither "
    "guaranteed physical boundaries nor statistically validated confidence intervals. Actual indoor "
    "particulate concentrations will be significantly higher during indoor combustion (cooking, incense, smoking)."
)


def calculate_indoor_screening(
    outdoor_pm2_5: float,
    room_area_sqm: float = 25.0,
    ceiling_height_m: float = 2.6,
    purifier_cadr_m3h: Optional[float] = 0.0,
) -> Dict[str, Any]:
    """Calculate scenario-based indoor PM2.5 screening estimates and dynamic clearance parameters."""
    c_out = max(0.0, float(outdoor_pm2_5))
    area = max(1.0, float(room_area_sqm))
    height = max(1.5, float(ceiling_height_m))
    volume = area * height
    cadr = max(0.0, float(purifier_cadr_m3h or 0.0))

    # --- Scenario 1: Favorable Building Envelope (Tight / Weather-Stripped) ---
    p_min = 0.40
    aer_min = 0.30
    k_dep_max = 0.30
    cadr_eff_fav = cadr  # 100% rated CADR
    lambda_fav = aer_min + k_dep_max + (cadr_eff_fav / volume)
    c_in_fav = (p_min * aer_min * c_out) / lambda_fav
    tau_fav_hr = 1.0 / lambda_fav
    tau_fav_min = tau_fav_hr * 60.0

    # --- Scenario 2: Unfavorable Building Envelope (Leaky / Unsealed) ---
    p_max = 0.85
    aer_max = 0.80
    k_dep_min = 0.15
    cadr_eff_unfav = 0.75 * cadr  # 75% effective CADR due to filter degradation/non-ideal mixing
    lambda_unfav = aer_max + k_dep_min + (cadr_eff_unfav / volume)
    c_in_unfav = (p_max * aer_max * c_out) / lambda_unfav
    tau_unfav_hr = 1.0 / lambda_unfav
    tau_unfav_min = tau_unfav_hr * 60.0

    # --- Purifier Engineering Screening Estimate ---
    equivalent_ach = round(cadr / volume, 2) if volume > 0 else 0.0
    if cadr > 0:
        purifier_context = (
            f"Calculated equivalent clean air changes per hour is {equivalent_ach} ACH. For comparison, "
            "the AHAM (Association of Home Appliance Manufacturers) Verifide standard bases room sizing "
            "on achieving 4.80 ACH (which requires a smoke CADR equal to 2/3 of room area assuming an 8 ft ceiling). "
            f"A calculated {equivalent_ach} ACH provides substantial particulate clearance but is an engineering "
            "screening estimate and does not constitute or imply official AHAM Verifide certification."
        )
    else:
        purifier_context = (
            "No active air purifier CADR was provided. Particulate clearance relies entirely on natural "
            "surface deposition and envelope exfiltration."
        )

    # --- Ventilation Guidance ---
    if c_out > 60.0:
        vent_status = "UNFAVORABLE"
        vent_advice = (
            "Outdoor particulate concentration exceeds safe limits (PM2.5 > 60 µg/m³). "
            "Keep windows closed to minimize outdoor particle infiltration."
        )
    elif c_out > 30.0:
        vent_status = "CAUTION"
        vent_advice = (
            "Moderate ambient particulate density. Limit natural ventilation to brief periods or "
            "ensure active HEPA filtration."
        )
    else:
        vent_status = "FAVORABLE"
        vent_advice = (
            "Outdoor air is within clean particulate thresholds (PM2.5 <= 30 µg/m³). "
            "Natural window cross-ventilation is favorable."
        )

    return {
        "outdoor_ambient_pm2_5": round(c_out, 2),
        "room_parameters": {
            "room_area_sqm": round(area, 1),
            "ceiling_height_m": round(height, 2),
            "room_volume_m3": round(volume, 2),
            "purifier_cadr_m3h": round(cadr, 1),
        },
        "scenario_based_heuristic_estimates": {
            "favorable_envelope_scenario_ug_m3": round(c_in_fav, 2),
            "unfavorable_envelope_scenario_ug_m3": round(c_in_unfav, 2),
            "indoor_data_type": "UNVERIFIED_ESTIMATE",
            "disclaimer": INDOOR_DISCLAIMER,
        },
        "dynamics": {
            "favorable_scenario": {
                "effective_clearance_rate_hr": round(lambda_fav, 3),
                "time_constant_tau_hours": round(tau_fav_hr, 3),
                "time_constant_tau_minutes": round(tau_fav_min, 1),
                "full_equilibration_time_3tau_minutes": round(tau_fav_min * 3.0, 1),
            },
            "unfavorable_scenario": {
                "effective_clearance_rate_hr": round(lambda_unfav, 3),
                "time_constant_tau_hours": round(tau_unfav_hr, 3),
                "time_constant_tau_minutes": round(tau_unfav_min, 1),
                "full_equilibration_time_3tau_minutes": round(tau_unfav_min * 3.0, 1),
            },
        },
        "purifier_engineering_estimate": {
            "room_volume_m3": round(volume, 2),
            "cadr_m3h": round(cadr, 1),
            "equivalent_ach": equivalent_ach,
            "engineering_context": purifier_context,
        },
        "ventilation_status": {
            "status": vent_status,
            "advisory": vent_advice,
        },
    }
