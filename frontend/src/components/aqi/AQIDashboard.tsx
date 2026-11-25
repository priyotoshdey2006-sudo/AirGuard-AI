import React from 'react';
import { CurrentAQI } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import { AlertCircle, Wind, Info, Activity, ShieldCheck, Droplets, Sun, Sparkles } from 'lucide-react';

interface Props {
  data: CurrentAQI | null;
  loading: boolean;
  onRefresh: () => void;
}

export const AQIDashboard: React.FC<Props> = ({ data, loading, onRefresh }) => {
  if (loading && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[420px] text-slate-400 gap-4">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 rounded-full border-2 border-emerald-500/20" />
          <div className="absolute inset-0 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin" />
        </div>
        <p className="text-xs font-semibold tracking-wide uppercase text-slate-400 animate-pulse">
          Calibrating Atmospheric Sensors...
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="liquid-glass-card p-8 rounded-3xl text-center max-w-md mx-auto my-12 border border-white/[0.08]">
        <AlertCircle className="w-12 h-12 text-amber-400 mx-auto mb-3 drop-shadow-[0_0_12px_rgba(245,158,11,0.3)]" />
        <h3 className="text-base font-bold text-white">Atmospheric Data Unavailable</h3>
        <p className="text-xs text-slate-400 mt-1.5 mb-5 leading-relaxed">
          Unable to establish connection with Open-Meteo atmospheric model service.
        </p>
        <button
          onClick={onRefresh}
          className="liquid-glass-control px-4 py-2 rounded-xl text-xs font-semibold text-emerald-300 hover:text-white"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Safe extraction of geographical coordinates
  const latitude =
    typeof data.latitude === 'number'
      ? data.latitude
      : typeof data.location?.latitude === 'number'
      ? data.location.latitude
      : null;

  const longitude =
    typeof data.longitude === 'number'
      ? data.longitude
      : typeof data.location?.longitude === 'number'
      ? data.location.longitude
      : null;

  // Safe extraction of AQI value without fabricating readings
  const aqiValue =
    typeof data.aqi_us === 'number'
      ? data.aqi_us
      : typeof data.us_epa_model_proxy?.proxy_index === 'number'
      ? data.us_epa_model_proxy.proxy_index
      : typeof data.cpcb_model_proxy?.proxy_index === 'number'
      ? data.cpcb_model_proxy.proxy_index
      : null;

  // Safe determination of category and accent color
  const categoryColor =
    data.category_color ||
    (aqiValue == null
      ? '#94a3b8'
      : aqiValue <= 50
      ? '#10b981'
      : aqiValue <= 100
      ? '#eab308'
      : aqiValue <= 150
      ? '#f97316'
      : aqiValue <= 200
      ? '#ef4444'
      : aqiValue <= 300
      ? '#a855f7'
      : '#7f1d1d');

  const categoryName =
    data.category ||
    data.us_epa_model_proxy?.category ||
    data.cpcb_model_proxy?.category ||
    (aqiValue != null
      ? aqiValue <= 50
        ? 'Good'
        : aqiValue <= 100
        ? 'Moderate'
        : aqiValue <= 150
        ? 'Unhealthy for Sensitive Groups'
        : aqiValue <= 200
        ? 'Unhealthy'
        : aqiValue <= 300
        ? 'Very Unhealthy'
        : 'Hazardous'
      : 'Data Unavailable');

  const dominantPollutant = (
    data.dominant_pollutant ||
    data.us_epa_model_proxy?.dominant_pollutant ||
    data.cpcb_model_proxy?.dominant_pollutant ||
    'PM2.5'
  ).toUpperCase();

  const aqiEuropean =
    typeof data.aqi_european === 'number'
      ? data.aqi_european
      : typeof data.cpcb_model_proxy?.proxy_index === 'number'
      ? data.cpcb_model_proxy.proxy_index
      : null;

  const formattedTime = (() => {
    const rawTime =
      data.timestamp ||
      (data as any).provenance?.model_valid_local ||
      (data as any).provenance?.model_valid_utc;
    if (!rawTime) return 'Recent';
    const date = new Date(rawTime);
    return isNaN(date.getTime())
      ? 'Recent'
      : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  })();

  const formatPollutantValue = (val: number | null | undefined): string => {
    if (val == null) return '—';
    return Number.isInteger(val) ? val.toString() : val.toFixed(1);
  };

  // Safe percentage calculation for Apple circular radial gauge (0 to 500 AQI scale)
  const aqiPercentage = Math.min(100, Math.max(0, ((aqiValue || 0) / 300) * 100));
  const strokeDashoffset = 283 - (283 * aqiPercentage) / 100;

  const pollutantsList = [
    {
      code: 'PM2.5',
      name: 'Fine Inhalable Particles',
      value: data.pollutants?.pm2_5,
      unit: 'µg/m³',
      whoLimit: '15 µg/m³',
      ratio: data.pollutants?.pm2_5 != null ? Math.min(100, (data.pollutants.pm2_5 / 35) * 100) : 0,
      desc: 'Microscopic particulates that penetrate deep into alveolar lung tissues and enter the bloodstream.',
      isHigh: data.pollutants?.pm2_5 != null && data.pollutants.pm2_5 > 35,
    },
    {
      code: 'PM10',
      name: 'Coarse Road & Dust Particles',
      value: data.pollutants?.pm10,
      unit: 'µg/m³',
      whoLimit: '45 µg/m³',
      ratio: data.pollutants?.pm10 != null ? Math.min(100, (data.pollutants.pm10 / 50) * 100) : 0,
      desc: 'Inhalable mineral dust, road grit, and mechanical brake particulate affecting upper respiratory tract.',
      isHigh: data.pollutants?.pm10 != null && data.pollutants.pm10 > 50,
    },
    {
      code: 'O3',
      name: 'Ground-Level Ozone',
      value: data.pollutants?.o3,
      unit: 'µg/m³',
      whoLimit: '100 µg/m³',
      ratio: data.pollutants?.o3 != null ? Math.min(100, (data.pollutants.o3 / 100) * 100) : 0,
      desc: 'Secondary photochemical pollutant formed by sunlight reacting with vehicular NOx emissions.',
      isHigh: data.pollutants?.o3 != null && data.pollutants.o3 > 100,
    },
    {
      code: 'NO2',
      name: 'Nitrogen Dioxide',
      value: data.pollutants?.no2,
      unit: 'µg/m³',
      whoLimit: '25 µg/m³',
      ratio: data.pollutants?.no2 != null ? Math.min(100, (data.pollutants.no2 / 40) * 100) : 0,
      desc: 'Combustion byproduct from diesel engines causing airway inflammation and bronchial hyperreactivity.',
      isHigh: data.pollutants?.no2 != null && data.pollutants.no2 > 40,
    },
    {
      code: 'SO2',
      name: 'Sulfur Dioxide',
      value: data.pollutants?.so2,
      unit: 'µg/m³',
      whoLimit: '40 µg/m³',
      ratio: data.pollutants?.so2 != null ? Math.min(100, (data.pollutants.so2 / 40) * 100) : 0,
      desc: 'Heavy industrial exhaust originating from coal-fired power plants and high-sulfur fuel refining.',
      isHigh: data.pollutants?.so2 != null && data.pollutants.so2 > 40,
    },
    {
      code: 'CO',
      name: 'Carbon Monoxide',
      value: data.pollutants?.co,
      unit: 'mg/m³',
      whoLimit: '4 mg/m³',
      ratio: data.pollutants?.co != null ? Math.min(100, (data.pollutants.co / 4) * 100) : 0,
      desc: 'Incomplete fuel oxidation gas impairing blood oxygenation through carboxyhemoglobin binding.',
      isHigh: data.pollutants?.co != null && data.pollutants.co > 4,
    },
    {
      code: 'UV',
      name: 'Solar Ultraviolet Radiation',
      value: data.pollutants?.uv_index,
      unit: 'Index',
      whoLimit: '3-5 (Mod)',
      ratio: data.pollutants?.uv_index != null ? Math.min(100, (data.pollutants.uv_index / 8) * 100) : 0,
      desc: 'Direct solar erythemal exposure index indicating skin protection requirement during daytime.',
      isHigh: data.pollutants?.uv_index != null && data.pollutants.uv_index > 6,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Floating Header with Provenance Badge */}
      <div className="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              {data.location_name || data.location?.timezone || 'Atmospheric Station'}
            </h1>
            <ProvenanceBadge provenance={data.provenance || 'MODEL_ANALYSIS'} />
          </div>
          <p className="text-xs text-slate-300/80 mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
            <span>
              Coordinates: {latitude != null ? `${latitude.toFixed(4)}°N` : '—'}
              {longitude != null ? `, ${longitude.toFixed(4)}°E` : ''}
            </span>
            <span className="text-slate-600">•</span>
            <span>Source: {data.source_provider || 'Open-Meteo'} ({data.native_model || 'ECMWF CAMS 0.4° Grid'})</span>
            <span className="text-slate-600">•</span>
            <span>Model Valid: {formattedTime}</span>
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="liquid-glass-control self-start sm:self-auto flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white disabled:opacity-50"
        >
          <Wind className={`w-3.5 h-3.5 text-emerald-400 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Primary AQI Ring & Health Advisory Deck */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Apple-Inspired Circular Gauge Card */}
        <div className="lg:col-span-5 liquid-glass-card rounded-3xl p-6 sm:p-7 flex flex-col justify-between relative overflow-hidden">
          {/* Ambient Radial Specular Glow matching current AQI Color */}
          <div
            className="absolute -top-16 -right-16 w-56 h-56 rounded-full blur-3xl opacity-25 pointer-events-none transition-all duration-700"
            style={{ backgroundColor: categoryColor }}
            aria-hidden="true"
          />

          <div className="flex items-center justify-between relative z-10">
            <span className="text-xs uppercase font-bold tracking-wider text-slate-400">
              Air Quality Index
            </span>
            <span
              className="text-xs font-semibold px-2.5 py-0.5 rounded-full border shadow-sm"
              style={{
                backgroundColor: `${categoryColor}18`,
                color: categoryColor,
                borderColor: `${categoryColor}40`,
              }}
            >
              US EPA Standard
            </span>
          </div>

          {/* Concentric Gauge Visualization */}
          <div className="my-6 flex flex-col items-center justify-center relative z-10">
            <div className="relative w-48 h-48 flex items-center justify-center">
              {/* Outer SVG Ring */}
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                {/* Track */}
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.06)"
                  strokeWidth="7"
                />
                {/* Progress arc */}
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={categoryColor}
                  strokeWidth="7"
                  strokeDasharray="283"
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                  style={{
                    filter: `drop-shadow(0 0 8px ${categoryColor}80)`,
                  }}
                />
              </svg>

              {/* Center Values */}
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span
                  className="text-5xl font-black tracking-tight tabular-nums transition-colors duration-500"
                  style={{ color: categoryColor }}
                >
                  {aqiValue != null ? aqiValue : '—'}
                </span>
                <span className="text-xs font-bold text-slate-300 mt-1 uppercase tracking-wider">
                  {categoryName}
                </span>
                <span className="text-[10px] text-slate-400 mt-0.5">
                  Peak: <strong className="text-emerald-400 font-semibold">{dominantPollutant}</strong>
                </span>
              </div>
            </div>
          </div>

          {/* Secondary Index Dock (CAQI / CPCB Equivalent) */}
          <div className="relative z-10 pt-4 border-t border-white/[0.06] flex items-center justify-between text-xs text-slate-400">
            <span>European CAQI / CPCB Equivalent:</span>
            <span className="font-bold text-slate-200 tabular-nums">
              {aqiEuropean != null ? `${aqiEuropean} / 100` : 'Unavailable'}
            </span>
          </div>
        </div>

        {/* Clinical Advisory & Routine Impact Card */}
        <div className="lg:col-span-7 liquid-glass-card rounded-3xl p-6 sm:p-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <ShieldCheck className="w-3.5 h-3.5" />
              </div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Official Clinical Health Advisory
              </h2>
            </div>

            <p className="text-sm text-slate-200 leading-relaxed bg-midnight-950/60 p-4 rounded-2xl border border-white/[0.06] shadow-inner">
              {data.health_advice ||
                (aqiValue != null
                  ? aqiValue > 200
                    ? 'Severe air quality warning. Minimize outdoor exposure. Keep certified N95 respirators equipped if travelling outdoors and maintain active indoor HEPA filtration.'
                    : aqiValue > 150
                    ? 'Unhealthy atmospheric conditions. Sensitive individuals and children should avoid prolonged outdoor exertion. Shift strenuous cardio routines indoors.'
                    : aqiValue > 100
                    ? 'Unhealthy for sensitive groups. People with asthma or respiratory conditions should limit extended outdoor physical activity.'
                    : aqiValue > 50
                    ? 'Moderate air quality. Acceptable for general public, though unusually sensitive individuals may experience mild respiratory irritation during peak hours.'
                    : 'Air quality is satisfactory and poses little or no health risk. Favorable conditions for outdoor recreation and natural home ventilation.'
                  : 'Atmospheric measurement data currently unavailable. Please verify network connectivity.')}
            </p>
          </div>

          {/* Protocol Micro-Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
            <div className="liquid-glass-control p-3.5 rounded-2xl">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                Outdoor Exertion
              </div>
              <div className="text-xs font-semibold text-slate-100 mt-1 flex items-center gap-1.5">
                {aqiValue != null
                  ? aqiValue > 150
                    ? '❌ Shift Indoors'
                    : aqiValue > 100
                    ? '⚠️ Moderate Pace'
                    : '✅ Safe for Cardio'
                  : '—'}
              </div>
            </div>

            <div className="liquid-glass-control p-3.5 rounded-2xl">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                Mask Protocol
              </div>
              <div className="text-xs font-semibold text-slate-100 mt-1 flex items-center gap-1.5">
                {aqiValue != null
                  ? aqiValue > 150
                    ? '😷 N95 Respirator'
                    : aqiValue > 100
                    ? '😷 Surgical Mask'
                    : '🌱 No Mask Needed'
                  : '—'}
              </div>
            </div>

            <div className="liquid-glass-control p-3.5 rounded-2xl">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                Ventilation Plan
              </div>
              <div className="text-xs font-semibold text-slate-100 mt-1 flex items-center gap-1.5">
                {aqiValue != null
                  ? aqiValue > 150
                    ? '🔒 Seal Windows'
                    : aqiValue > 80
                    ? '⏱️ Midday Only'
                    : '🪟 Natural Airflow'
                  : '—'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Pollutants Grid with WHO Guideline Benchmarks */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Pollutant Breakdown & WHO Threshold Benchmarks</span>
          </h2>
          <span className="text-[11px] text-slate-400 hidden sm:inline font-mono">
            Calibrated via Open-Meteo Atmospheric Models
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {pollutantsList.map((p) => (
            <div
              key={p.code}
              className={`liquid-glass-card liquid-glass-hover p-4 sm:p-5 rounded-2xl flex flex-col justify-between ${
                p.isHigh ? 'border-amber-500/25' : ''
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-bold text-base text-white">{p.code}</span>
                  <span className="text-[10px] text-slate-400 font-mono px-2 py-0.5 rounded-md bg-white/[0.04] border border-white/[0.06]">
                    WHO: {p.whoLimit}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-0.5 truncate">{p.name}</div>

                <div className="my-3 flex items-baseline gap-1.5">
                  <span
                    className={`text-2xl sm:text-3xl font-black tabular-nums ${
                      p.isHigh ? 'text-amber-400' : 'text-emerald-400'
                    }`}
                  >
                    {formatPollutantValue(p.value)}
                  </span>
                  <span className="text-xs text-slate-400 font-medium">{p.unit}</span>
                </div>

                {/* Micro Ratio Bar */}
                <div className="w-full h-1 bg-white/[0.06] rounded-full overflow-hidden mb-2.5">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      p.isHigh ? 'bg-amber-400' : 'bg-emerald-400'
                    }`}
                    style={{ width: `${p.ratio}%` }}
                  />
                </div>
              </div>

              <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">
                {p.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Scientific Transparency & Provenance Dock */}
      <div className="liquid-glass-control rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-400 border border-white/[0.08]">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>
            <strong className="text-slate-300 font-semibold">Provenance Note:</strong> Values reflect numerical atmospheric composition reanalysis at native 0.4° grid centroid (~45 km resolution) from ECMWF CAMS via Open-Meteo, not direct continuous statutory CAAQMS sensor stations.
          </span>
        </div>
        <div className="shrink-0 text-[11px] text-slate-400 font-mono">
          Model Valid: {formattedTime}
        </div>
      </div>
    </div>
  );
};
