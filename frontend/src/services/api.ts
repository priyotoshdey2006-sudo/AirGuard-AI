import {
  CommunityReport,
  CurrentAQI,
  ForecastData,
  IndoorGuidance,
  RouteComparison,
  RoutinePlan,
  SensitivityLevel,
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  async getCurrentAQI(lat: number, lon: number): Promise<CurrentAQI> {
    const res = await fetch(`${API_BASE}/aqi/current?lat=${lat}&lon=${lon}`);
    return handleResponse<CurrentAQI>(res);
  },

  async getForecast(lat: number, lon: number): Promise<ForecastData> {
    const res = await fetch(`${API_BASE}/aqi/forecast?lat=${lat}&lon=${lon}`);
    return handleResponse<ForecastData>(res);
  },

  async getIndoorGuidance(
    lat: number,
    lon: number,
    roomSqft: number = 350,
    hasHepa: boolean = true
  ): Promise<IndoorGuidance> {
    const res = await fetch(
      `${API_BASE}/aqi/indoor-guidance?lat=${lat}&lon=${lon}&room_sqft=${roomSqft}&has_hepa_filter=${hasHepa}`
    );
    return handleResponse<IndoorGuidance>(res);
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
    sensitivity: string = 'NORMAL'
  ): Promise<{ reply: string; model_provider: string; suggested_followups: string[] }> {
    const res = await fetch(`${API_BASE}/assistant/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        latitude: lat,
        longitude: lon,
        sensitivity_level: sensitivity,
      }),
    });
    return handleResponse<{ reply: string; model_provider: string; suggested_followups: string[] }>(res);
  },
};
