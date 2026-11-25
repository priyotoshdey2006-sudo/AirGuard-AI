import {
  CommunityReport,
  CurrentAQI,
  ForecastData,
  IndoorGuidance,
  Pollutants,
  Provenance,
  RouteComparison,
  RoutinePlan,
  SensitivityLevel,
} from '../types';

// In production on Vercel, requests are dispatched to the deployed Render backend via VITE_API_BASE_URL.
// In local development, it falls back to '/api/v1' which is proxied by Vite to http://localhost:8000.
const rawBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');
const API_BASE = rawBase ? (rawBase.endsWith('/api/v1') ? rawBase : `${rawBase}/api/v1`) : '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText || res.statusText}`);
  }
  return res.json();
}

function extractPollutantConcentration(field: any): number | null {
  if (field == null) return null;
  if (typeof field === 'number') return isNaN(field) ? null : field;
  if (typeof field === 'object' && field.concentration !== undefined) {
    if (field.concentration === null) return null;
    const num = Number(field.concentration);
    return isNaN(num) ? null : num;
  }
  const parsed = Number(field);
  return isNaN(parsed) ? null : parsed;
}

function getCategoryColor(aqi: number | null | undefined): string {
  if (aqi == null) return '#94a3b8';
  if (aqi <= 50) return '#10b981';
  if (aqi <= 100) return '#eab308';
  if (aqi <= 150) return '#f97316';
  if (aqi <= 200) return '#ef4444';
  if (aqi <= 300) return '#a855f7';
  return '#7f1d1d';
}

function getHealthAdvice(category: string, aqi: number | null | undefined): string {
  if (aqi == null) return 'Atmospheric measurement data currently unavailable.';
  if (aqi > 200) {
    return 'Severe air quality warning. Minimize outdoor exposure. Keep certified N95 respirators equipped if travelling outdoors and maintain active indoor HEPA filtration.';
  }
  if (aqi > 150) {
    return 'Unhealthy atmospheric conditions. Sensitive individuals and children should avoid prolonged outdoor exertion. Shift strenuous cardio routines indoors.';
  }
  if (aqi > 100) {
    return 'Unhealthy for sensitive groups. People with asthma or respiratory conditions should limit extended outdoor physical activity.';
  }
  if (aqi > 50) {
    return 'Moderate air quality. Acceptable for general public, though unusually sensitive individuals may experience mild respiratory irritation during peak hours.';
  }
  return 'Air quality is satisfactory and poses little or no health risk. Favorable conditions for outdoor recreation and natural home ventilation.';
}

export const api = {
  async getCurrentAQI(lat: number, lon: number): Promise<CurrentAQI> {
    const res = await fetch(`${API_BASE}/aqi/current?lat=${lat}&lon=${lon}`);
    const raw = await handleResponse<any>(res);

    // Support both flattened and nested FastAPI CurrentAQIResponse schemas
    const latitude = typeof raw.latitude === 'number' ? raw.latitude : (raw.location?.latitude ?? lat);
    const longitude = typeof raw.longitude === 'number' ? raw.longitude : (raw.location?.longitude ?? lon);
    const aqiUs =
      typeof raw.aqi_us === 'number'
        ? raw.aqi_us
        : raw.us_epa_model_proxy?.proxy_index ?? raw.cpcb_model_proxy?.proxy_index ?? null;
    const aqiEuropean =
      typeof raw.aqi_european === 'number'
        ? raw.aqi_european
        : raw.cpcb_model_proxy?.proxy_index ?? raw.us_epa_model_proxy?.proxy_index ?? null;
    const category =
      raw.category ||
      raw.us_epa_model_proxy?.category ||
      raw.cpcb_model_proxy?.category ||
      'Moderate';
    const dominantPollutant =
      raw.dominant_pollutant ||
      raw.us_epa_model_proxy?.dominant_pollutant ||
      raw.cpcb_model_proxy?.dominant_pollutant ||
      'pm2_5';
    const provStr = raw.provenance?.data_provenance || raw.provenance || 'MODEL_ANALYSIS';
    const provenance: Provenance =
      provStr === 'MODEL_FORECAST' || provStr === 'FORECAST'
        ? 'FORECAST'
        : provStr === 'UNVERIFIED_ESTIMATE' || provStr === 'ESTIMATED'
        ? 'ESTIMATED'
        : 'MODEL_ANALYSIS';

    const rawPollutants = raw.pollutants || {};
    const pollutants: Pollutants = {
      pm2_5: extractPollutantConcentration(rawPollutants.pm2_5),
      pm10: extractPollutantConcentration(rawPollutants.pm10),
      o3: extractPollutantConcentration(rawPollutants.o3),
      no2: extractPollutantConcentration(rawPollutants.no2),
      so2: extractPollutantConcentration(rawPollutants.so2),
      co: extractPollutantConcentration(rawPollutants.co),
      uv_index: extractPollutantConcentration(rawPollutants.uv_index),
    };

    return {
      latitude,
      longitude,
      location_name: raw.location_name || raw.location?.timezone || 'Current Location',
      aqi_us: aqiUs,
      aqi_european: aqiEuropean,
      category,
      category_color: raw.category_color || getCategoryColor(aqiUs),
      dominant_pollutant: dominantPollutant,
      pollutants,
      health_advice: raw.health_advice || getHealthAdvice(category, aqiUs),
      provenance,
      timestamp:
        raw.timestamp ||
        raw.provenance?.model_valid_local ||
        raw.provenance?.model_valid_utc ||
        new Date().toISOString(),
      location: raw.location,
      us_epa_model_proxy: raw.us_epa_model_proxy,
      cpcb_model_proxy: raw.cpcb_model_proxy,
      source_provider: raw.provenance?.source_provider || 'Open-Meteo Air Quality API',
      native_model: raw.provenance?.native_atmospheric_model || 'ECMWF CAMS Global (IFS-AER)',
      native_resolution: raw.provenance?.native_spatial_resolution || '0.4° (~45 km)',
      model_valid_utc: raw.provenance?.model_valid_utc,
      model_valid_local: raw.provenance?.model_valid_local,
    };
  },

  async getForecast(lat: number, lon: number): Promise<ForecastData> {
    const res = await fetch(`${API_BASE}/aqi/forecast?lat=${lat}&lon=${lon}`);
    const raw = await handleResponse<any>(res);

    const hourly = (raw.forecast_series || raw.hourly || []).map((item: any) => ({
      time: item.time_local || item.time_utc || item.time || '',
      aqi_us: item.us_proxy_index ?? item.cpcb_proxy_index ?? item.aqi_us ?? 0,
      pm2_5: item.pm2_5 ?? 0,
      pm10: item.pm10 ?? 0,
      category: item.category || 'Moderate',
    }));

    const provStr = raw.provenance?.data_provenance || raw.provenance || 'FORECAST';
    const provenance: Provenance =
      provStr === 'MODEL_FORECAST' || provStr === 'FORECAST'
        ? 'FORECAST'
        : provStr === 'UNVERIFIED_ESTIMATE' || provStr === 'ESTIMATED'
        ? 'ESTIMATED'
        : 'OBSERVED';

    return {
      latitude: raw.latitude ?? raw.location?.latitude ?? lat,
      longitude: raw.longitude ?? raw.location?.longitude ?? lon,
      hourly,
      daily: raw.daily || [],
      provenance,
    };
  },

  async getIndoorGuidance(
    lat: number,
    lon: number,
    roomSqft: number = 350,
    hasHepa: boolean = true
  ): Promise<IndoorGuidance> {
    const roomAreaSqm = Math.max(5.0, Number((roomSqft * 0.092903).toFixed(1)));
    const cadr = hasHepa ? 250.0 : 0.0;
    try {
      const res = await fetch(
        `${API_BASE}/indoor/screening?lat=${lat}&lon=${lon}&room_area_sqm=${roomAreaSqm}&ceiling_height_m=2.6&purifier_cadr_m3h=${cadr}`
      );
      if (res.ok) {
        const raw = await res.json();
        const outdoorPm25 = raw.outdoor_ambient_pm2_5 ?? 45.0;
        const indoorPm25 = hasHepa
          ? raw.scenario_based_heuristic_estimates?.favorable_envelope_scenario_ug_m3 ?? outdoorPm25 * 0.25
          : raw.scenario_based_heuristic_estimates?.unfavorable_envelope_scenario_ug_m3 ?? outdoorPm25 * 0.75;
        const ach = raw.purifier_engineering_estimate?.equivalent_ach ?? (hasHepa ? 3.5 : 0.5);

        return {
          outdoor_aqi: Math.round(outdoorPm25 * 1.5),
          estimated_indoor_aqi: Math.round(indoorPm25 * 1.5),
          indoor_category: indoorPm25 < 15 ? 'Good' : indoorPm25 < 35 ? 'Moderate' : 'Unhealthy',
          window_advice:
            outdoorPm25 > 60
              ? 'Keep windows closed. Ambient particulate levels exceed safe ventilation threshold.'
              : 'Safe to open windows during midday convection window.',
          safe_ventilation_windows: [
            {
              start_time: '12:00 PM',
              end_time: '03:00 PM',
              expected_outdoor_aqi: Math.round(outdoorPm25 * 1.2),
              recommendation: 'Optimal atmospheric boundary layer ventilation',
            },
          ],
          hepa_runtime_recommendation_hours: hasHepa ? (outdoorPm25 > 100 ? 16 : 8) : 0,
          air_cleaner_speed: hasHepa ? (outdoorPm25 > 100 ? 'HIGH' : 'MEDIUM / AUTO') : 'N/A',
          tips: [
            `Purifier provides approximately ${ach.toFixed(1)} air changes per hour (ACH).`,
            'Ensure pre-filters are vacuumed bi-weekly to prevent CADR airflow degradation.',
            'Maintain indoor relative humidity between 30% and 50% for optimal respiratory comfort.',
          ],
          provenance: 'ESTIMATED',
        };
      }
    } catch (e) {
      console.warn('Indoor guidance endpoint fallback:', e);
    }

    return {
      outdoor_aqi: 120,
      estimated_indoor_aqi: hasHepa ? 35 : 85,
      indoor_category: hasHepa ? 'Good' : 'Moderate',
      window_advice: 'Ventilate during afternoon hours when surface inversion breaks.',
      safe_ventilation_windows: [
        {
          start_time: '01:00 PM',
          end_time: '04:00 PM',
          expected_outdoor_aqi: 95,
          recommendation: 'Afternoon atmospheric mixing window',
        },
      ],
      hepa_runtime_recommendation_hours: hasHepa ? 12 : 0,
      air_cleaner_speed: hasHepa ? 'AUTO' : 'OFF',
      tips: [
        'Run HEPA filtration during sleeping hours to minimize nocturnal particulate intake.',
        'Seal drafty door thresholds and exterior windows during smog alerts.',
      ],
      provenance: 'ESTIMATED',
    };
  },

  async getDailyRoutine(
    lat: number,
    lon: number,
    sensitivity: SensitivityLevel,
    activities: string[]
  ): Promise<RoutinePlan> {
    const res = await fetch(`${API_BASE}/recommendations/daily-routine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        sensitivity_level: sensitivity,
        planned_activities: activities,
      }),
    });
    return handleResponse<RoutinePlan>(res);
  },

  async compareRoutes(
    originLat: number,
    originLon: number,
    destLat: number,
    destLon: number,
    originName: string = 'Origin',
    destName: string = 'Destination'
  ): Promise<RouteComparison> {
    const res = await fetch(`${API_BASE}/transport/compare-routes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        origin_lat: originLat,
        origin_lon: originLon,
        dest_lat: destLat,
        dest_lon: destLon,
        origin_name: originName,
        dest_name: destName,
      }),
    });
    return handleResponse<RouteComparison>(res);
  },

  async getCommunityReports(
    lat?: number,
    lon?: number,
    radiusKm: number = 50,
    category?: string
  ): Promise<{ total: number; reports: CommunityReport[] }> {
    let url = `${API_BASE}/community/reports?radius_km=${radiusKm}`;
    if (lat !== undefined && lon !== undefined) {
      url += `&lat=${lat}&lon=${lon}`;
    }
    if (category) {
      url += `&category=${category}`;
    }
    const res = await fetch(url);
    return handleResponse<{ total: number; reports: CommunityReport[] }>(res);
  },

  async submitCommunityReport(report: {
    title: string;
    description: string;
    category: string;
    severity: number;
    latitude: number;
    longitude: number;
    reporter_name?: string;
  }): Promise<CommunityReport> {
    const res = await fetch(`${API_BASE}/community/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(report),
    });
    return handleResponse<CommunityReport>(res);
  },

  async upvoteReport(reportId: string): Promise<{ id: string; upvotes_count: number; status: string }> {
    const res = await fetch(`${API_BASE}/community/reports/${reportId}/upvote`, {
      method: 'POST',
    });
    return handleResponse<{ id: string; upvotes_count: number; status: string }>(res);
  },

  async sendChatMessage(
    message: string,
    lat?: number,
    lon?: number,
    sensitivity: string = 'NORMAL',
    currentAqi?: number | null,
    category?: string,
    dominantPollutant?: string,
    locationName?: string
  ): Promise<{ reply: string; model_provider: string; suggested_followups: string[] }> {
    const res = await fetch(`${API_BASE}/assistant/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        latitude: lat,
        longitude: lon,
        sensitivity_level: sensitivity,
        current_aqi: currentAqi != null ? currentAqi : undefined,
        category,
        dominant_pollutant: dominantPollutant,
        location_name: locationName,
      }),
    });
    return handleResponse<{ reply: string; model_provider: string; suggested_followups: string[] }>(res);
  },
};
