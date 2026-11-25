"""Pydantic v2 schemas for Indoor Air Quality (IAQ) screening and dynamic response parameters."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class IndoorScreeningRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    room_area_sqm: float = Field(25.0, ge=1.0, le=1000.0, description="Floor area in square meters")
    ceiling_height_m: float = Field(2.6, ge=1.5, le=10.0, description="Ceiling height in meters")
    purifier_cadr_m3h: Optional[float] = Field(0.0, ge=0.0, le=5000.0, description="Rated Clean Air Delivery Rate (m³/hr)")


class ScenarioEstimates(BaseModel):
    favorable_envelope_scenario_ug_m3: float
    unfavorable_envelope_scenario_ug_m3: float
    indoor_data_type: str = "UNVERIFIED_ESTIMATE"
    disclaimer: str


class DynamicsScenario(BaseModel):
    effective_clearance_rate_hr: float
    time_constant_tau_hours: float
    time_constant_tau_minutes: float
    full_equilibration_time_3tau_minutes: float


class DynamicsInfo(BaseModel):
    favorable_scenario: DynamicsScenario
    unfavorable_scenario: DynamicsScenario


class PurifierEngineeringEstimate(BaseModel):
    room_volume_m3: float
    cadr_m3h: float
    equivalent_ach: float
    engineering_context: str


class VentilationStatus(BaseModel):
    status: str
    advisory: str


class RoomParameters(BaseModel):
    room_area_sqm: float
    ceiling_height_m: float
    room_volume_m3: float
    purifier_cadr_m3h: float


class IndoorScreeningResponse(BaseModel):
    outdoor_ambient_pm2_5: float
    room_parameters: RoomParameters
    scenario_based_heuristic_estimates: ScenarioEstimates
    dynamics: DynamicsInfo
    purifier_engineering_estimate: PurifierEngineeringEstimate
    ventilation_status: VentilationStatus
