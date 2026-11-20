"""Environmental impact and sustainable transportation calculator."""

from typing import List
from app.schemas.transport import RouteCompareRequest, RouteCompareResponse, RouteOption
from app.services.geo_service import haversine_distance_km

# CO2 emission factors in kg CO2 per passenger-kilometer (IPCC / DEFRA averages)
EMISSION_FACTORS = {
    "WALK": 0.0,
    "BICYCLE": 0.0,
    "ELECTRIC_BUS": 0.035,
    "METRO": 0.025,
    "EV": 0.045,
    "ICE_CAR": 0.170,  # Baseline standard gasoline vehicle
}

# Average travel speeds in urban corridors (km/h)
MODE_SPEEDS_KMH = {
    "WALK": 4.5,
    "BICYCLE": 15.0,
    "ELECTRIC_BUS": 22.0,
    "METRO": 35.0,
    "EV": 30.0,
    "ICE_CAR": 28.0,
}

# Minute ventilation rate (Liters of air inhaled per minute during activity)
# Walking/Cycling involves higher physical exertion and higher respiratory volume.
VENTILATION_RATES = {
    "WALK": 18.0,
    "BICYCLE": 32.0,
    "ELECTRIC_BUS": 9.0,
    "METRO": 7.5,
    "EV": 7.0,
    "ICE_CAR": 8.0,
}

# Cabin / vehicle filtration efficiency factor (1.0 = full ambient exposure, 0.4 = filtered HVAC cabin)
CABIN_FILTRATION = {
    "WALK": 1.0,
    "BICYCLE": 1.0,
    "ELECTRIC_BUS": 0.6,
    "METRO": 0.45,
    "EV": 0.35,  # HEPA cabin filter
    "ICE_CAR": 0.5,
}


class ImpactCalculatorService:
    @staticmethod
    def calculate_route_comparison(
        request: RouteCompareRequest, current_ambient_aqi: int = 80
    ) -> RouteCompareResponse:
        """Calculate multi-modal travel duration, CO2 impact, and inhaled AQI exposure."""
        distance_km = request.distance_km
        if not distance_km:
            distance_km = haversine_distance_km(
                request.origin_lat, request.origin_lon, request.dest_lat, request.dest_lon
            )
            # Urban road winding factor (~1.25x direct Euclidean distance)
            distance_km = max(0.5, round(distance_km * 1.25, 2))

        # Baseline ICE Car emissions
        baseline_car_co2 = distance_km * EMISSION_FACTORS["ICE_CAR"]

        options: List[RouteOption] = []
        labels = {
            "WALK": "Walking",
            "BICYCLE": "Cycling / E-Bike",
            "ELECTRIC_BUS": "Electric Bus",
            "METRO": "Metro Transit",
            "EV": "Electric Car (EV)",
            "ICE_CAR": "Gasoline Car (Baseline)",
        }

        for mode, speed in MODE_SPEEDS_KMH.items():
            # Filter out walking for unrealistic distances (> 8 km) or cycling (> 25 km)
            if mode == "WALK" and distance_km > 7.0:
                continue
            if mode == "BICYCLE" and distance_km > 25.0:
                continue

            duration_hours = distance_km / speed
            duration_minutes = round(duration_hours * 60.0, 1)

            mode_co2 = round(distance_km * EMISSION_FACTORS[mode], 3)
            co2_saved = round(max(0.0, baseline_car_co2 - mode_co2), 3)

            # Inhaled exposure score = Duration (min) * Minute Ventilation Rate (L/min) * Ambient AQI * Infiltration
            # Normalized to index score
            inhaled_liters = duration_minutes * VENTILATION_RATES[mode] * CABIN_FILTRATION[mode]
            exposure_score = round((inhaled_liters * current_ambient_aqi) / 1000.0, 1)

            if exposure_score < 25.0:
                exp_level = "LOW"
            elif exposure_score < 60.0:
                exp_level = "MODERATE"
            else:
                exp_level = "HIGH"

            # Intelligence logic for recommendation:
            # If AQI is hazardous (>200), do NOT recommend outdoor cycling/walking despite 0 CO2
            recommended = False
            reason = ""
            if current_ambient_aqi > 150:
                if mode in ["METRO", "EV"]:
                    recommended = True
                    reason = "Filtered cabin protects lungs during high ambient pollution"
            else:
                if mode in ["METRO", "ELECTRIC_BUS", "BICYCLE"]:
                    recommended = True
                    reason = "Optimal balance of zero direct emissions and healthy commute"

            options.append(
                RouteOption(
                    mode=mode,
                    mode_label=labels.get(mode, mode),
                    duration_minutes=duration_minutes,
                    co2_kg=mode_co2,
                    co2_saved_kg=co2_saved,
                    aqi_exposure_score=exposure_score,
                    exposure_level=exp_level,
                    recommended=recommended,
                    recommendation_reason=reason,
                )
            )

        # Trees equivalent: 1 mature tree absorbs ~21.77 kg CO2 per year
        max_co2_saved = max([opt.co2_saved_kg for opt in options], default=0.0)
        trees_equiv = round(max_co2_saved / 21.77, 4)

        return RouteCompareResponse(
            distance_km=distance_km,
            origin_name=request.origin_name,
            dest_name=request.dest_name,
            options=options,
            cleanest_mode="METRO" if current_ambient_aqi > 150 else "BICYCLE",
            lowest_carbon_mode="BICYCLE" if distance_km <= 10.0 else "METRO",
            total_trees_equivalent=trees_equiv,
        )


impact_calculator = ImpactCalculatorService()
