export type Provenance = 'OBSERVED' | 'FORECAST' | 'ESTIMATED' | 'MODEL_ANALYSIS';

export type SensitivityLevel =
  | 'NORMAL'
  | 'ASTHMATIC'
  | 'CARDIOVASCULAR'
  | 'ELDERLY'
  | 'CHILD'
  | 'ATHLETE';

export interface Pollutants {
  pm2_5: number | null;
  pm10: number | null;
  o3: number | null;
  no2: number | null;
  so2: number | null;
  co: number | null;
  uv_index: number | null;
}

type float = number;

export interface CurrentAQI {
  latitude: number;
  longitude: number;
  location_name: string;
  aqi_us: number | null;
  aqi_european: number | null;
  category: string;
  category_color: string;
  dominant_pollutant: string;
  pollutants: Pollutants;
  health_advice: string;
  provenance: Provenance;
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
    grid_latitude?: number | null;
    grid_longitude?: number | null;
    timezone?: string;
  };
  us_epa_model_proxy?: {
    proxy_index?: number | null;
    category?: string;
    dominant_pollutant?: string;
  };
  cpcb_model_proxy?: {
    proxy_index?: number | null;
    category?: string;
    dominant_pollutant?: string;
  };
  source_provider?: string;
  native_model?: string;
  native_resolution?: string;
  model_valid_utc?: string;
  model_valid_local?: string;
}

export interface HourlyForecast {
  time: string;
  aqi_us: number;
  pm2_5: number;
  pm10: number;
  category: string;
}

export interface DailyForecast {
  date: string;
  max_aqi: number;
  min_aqi: number;
  dominant_pollutant: string;
  category: string;
}

export interface ForecastData {
  latitude: number;
  longitude: number;
  hourly: HourlyForecast[];
  daily: DailyForecast[];
  provenance: Provenance;
}

export interface ActivityWindow {
  activity_name: string;
  optimal_time: string;
  expected_aqi: number;
  safety_rating: 'SAFE' | 'CAUTION' | 'AVOID';
  mask_recommendation: 'NONE' | 'SURGICAL' | 'N95_REQUIRED';
  mitigation_tips: string;
}

export interface RoutinePlan {
  sensitivity_level: string;
  overall_risk_assessment: string;
  daily_summary: string;
  activity_windows: ActivityWindow[];
  action_items: string[];
  indoor_guidance: string;
  model_provider: string;
  provenance: Provenance;
}

export interface SafeVentilationWindow {
  start_time: string;
  end_time: string;
  expected_outdoor_aqi: number;
  recommendation: string;
}

export interface IndoorGuidance {
  outdoor_aqi: number;
  estimated_indoor_aqi: number;
  indoor_category: string;
  window_advice: string;
  safe_ventilation_windows: SafeVentilationWindow[];
  hepa_runtime_recommendation_hours: number;
  air_cleaner_speed: string;
  tips: string[];
  provenance: Provenance;
}

export interface RouteOption {
  mode: string;
  mode_label: string;
  duration_minutes: number;
  co2_kg: number;
  co2_saved_kg: number;
  aqi_exposure_score: number;
  exposure_level: 'LOW' | 'MODERATE' | 'HIGH';
  recommended: boolean;
  recommendation_reason: string;
}

export interface RouteComparison {
  distance_km: number;
  origin_name: string;
  dest_name: string;
  options: RouteOption[];
  cleanest_mode: string;
  lowest_carbon_mode: string;
  total_trees_equivalent: number;
}

export interface CommunityReport {
  id: string;
  title: string;
  description: string;
  category: string;
  severity: number;
  latitude: number;
  longitude: number;
  image_url?: string;
  status: string;
  upvotes_count: number;
  reporter_name: string;
  created_at: string;
  distance_km?: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  model_provider?: string;
}
