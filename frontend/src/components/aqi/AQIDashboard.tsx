import React from 'react';
import { CurrentAQI } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import { AlertCircle, CheckCircle2, Info, Wind, Sun, Droplets } from 'lucide-react';

interface Props {
  data: CurrentAQI | null;
  loading: boolean;
  onRefresh: () => void;
}

export const AQIDashboard: React.FC<Props> = ({ data, loading, onRefresh }) => {
  if (loading && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-slate-400 gap-3">
        <div className="w-10 h-10 border-4 border-teal-500/20 border-t-teal-400 rounded-full animate-spin" />
        <p className="text-sm font-medium">Fetching real-time atmospheric measurements...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-md mx-auto my-12">
        <AlertCircle className="w-12 h-12 text-amber-400 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-200">Unable to load air quality data</h3>
        <p className="text-xs text-slate-400 mt-1 mb-4">Please verify network connectivity or select another city.</p>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs rounded-lg transition-colors"
        >
          Retry Fetch
        </button>
      </div>
    );
  }

  const pollutantsList = [
    {
      code: 'PM2.5',
      name: 'Fine Particulate Matter',
      value: data.pollutants.pm2_5,
      unit: 'µg/m³',
      whoLimit: '15 µg/m³ (24h)',
      desc: 'Penetrates deep into alveolar lung tissue and bloodstream',
      isHigh: data.pollutants.pm2_5 > 35,
    },
    {
      code: 'PM10',
      name: 'Coarse Particulates',
      value: data.pollutants.pm10,
      unit: 'µg/m³',
      whoLimit: '45 µg/m³ (24h)',
      desc: 'Inhalable dust, pollen, and vehicular brake dust particles',
      isHigh: data.pollutants.pm10 > 50,
    },
    {
      code: 'O3',
      name: 'Surface Ozone',
      value: data.pollutants.o3,
      unit: 'µg/m³',
      whoLimit: '100 µg/m³ (8h)',
      desc: 'Photochemical oxidant formed by sunlight and smog',
      isHigh: data.pollutants.o3 > 100,
    },
    {
      code: 'NO2',
      name: 'Nitrogen Dioxide',
      value: data.pollutants.no2,
      unit: 'µg/m³',
      whoLimit: '25 µg/m³ (24h)',
      desc: 'Emitted from vehicle exhausts and thermal combustion',
      isHigh: data.pollutants.no2 > 40,
    },
    {
      code: 'SO2',
      name: 'Sulfur Dioxide',
      value: data.pollutants.so2,
      unit: 'µg/m³',
      whoLimit: '40 µg/m³ (24h)',
      desc: 'Originates from coal power plants and diesel refineries',
      isHigh: data.pollutants.so2 > 40,
    },
    {
      code: 'CO',
      name: 'Carbon Monoxide',
      value: data.pollutants.co,
      unit: 'µg/m³',
      whoLimit: '4,000 µg/m³ (24h)',
      desc: 'Colorless toxic gas from incomplete engine combustion',
      isHigh: data.pollutants.co > 2000,
    },
    {
      code: 'UV',
      name: 'Solar UV Index',
      value: data.pollutants.uv_index,
      unit: 'Index',
      whoLimit: '3-5 (Moderate)',
      desc: 'Sun exposure risk factor requiring skin and eye protection',
      isHigh: data.pollutants.uv_index > 6,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Bar with Location, Provenance, and Timestamp */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">{data.location_name}</h2>
            <ProvenanceBadge provenance={data.provenance} />
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Coordinates: {data.latitude.toFixed(4)}°N, {data.longitude.toFixed(4)}°E • Last updated:{' '}
            {new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="self-start sm:self-auto flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors border border-slate-700 disabled:opacity-50"
        >
          <Wind className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh AQI</span>
        </button>
      </div>

      {/* Primary AQI Card & Clinical Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main AQI Gauge Card */}
        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-bold tracking-wider text-slate-400">Air Quality Index</span>
            <span
              className="text-xs font-semibold px-2.5 py-0.5 rounded-full"
              style={{ backgroundColor: `${data.category_color}25`, color: data.category_color }}
            >
              US EPA Standard
            </span>
          </div>

          <div className="my-6 text-center">
            <div
              className="text-6xl font-black tracking-tight"
              style={{ color: data.category_color }}
            >
              {data.aqi_us}
            </div>
            <div className="text-base font-bold text-slate-100 mt-1">{data.category}</div>
            <div className="text-xs text-slate-400 mt-0.5">
              Primary Pollutant: <span className="text-teal-400 font-semibold">{data.dominant_pollutant.toUpperCase()}</span>
            </div>
          </div>

          <div className="border-t border-slate-800/80 pt-4 flex items-center justify-between text-xs text-slate-400">
            <span>European CAQI Equivalent:</span>
            <span className="font-bold text-slate-200">{data.aqi_european} / 100</span>
          </div>
        </div>

        {/* Health Advisory & Routine Impact Card */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-4 h-4 text-teal-400" />
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                Official Clinical Health Advisory
              </h3>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              {data.health_advice}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
            <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800/80">
              <div className="text-[11px] text-slate-400 uppercase font-bold">Outdoor Workouts</div>
              <div className="text-xs font-semibold text-slate-200 mt-1">
                {data.aqi_us > 150 ? '❌ Shift Indoors' : data.aqi_us > 100 ? '⚠️ Moderate Exertion' : '✅ Safe for Cardio'}
              </div>
            </div>

            <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800/80">
              <div className="text-[11px] text-slate-400 uppercase font-bold">Mask Requirement</div>
              <div className="text-xs font-semibold text-slate-200 mt-1">
                {data.aqi_us > 150 ? '😷 N95 Respirator Required' : data.aqi_us > 100 ? '😷 Surgical Mask Advised' : '🌱 No Mask Needed'}
              </div>
            </div>

            <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800/80">
              <div className="text-[11px] text-slate-400 uppercase font-bold">Home Ventilation</div>
              <div className="text-xs font-semibold text-slate-200 mt-1">
                {data.aqi_us > 150 ? '🔒 Seal Doors & Windows' : data.aqi_us > 80 ? '⏱️ Ventilate at Midday Only' : '🪟 Natural Airflow Safe'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Pollutants Grid with WHO Guidance */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Wind className="w-4 h-4 text-teal-400" />
            <span>Pollutant Breakdown & WHO Threshold Benchmarks</span>
          </h3>
          <span className="text-xs text-slate-500 hidden sm:inline">Calibrated via Open-Meteo Atmospheric Models</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {pollutantsList.map((p) => (
            <div
              key={p.code}
              className={`glass-panel p-4 rounded-xl border transition-all ${
                p.isHigh ? 'border-amber-500/30 bg-amber-500/5' : 'border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-base text-slate-200">{p.code}</span>
                <span className="text-[11px] text-slate-400 font-mono">WHO: {p.whoLimit}</span>
              </div>
              <div className="text-xs text-slate-400 mt-0.5 truncate">{p.name}</div>

              <div className="my-2.5 flex items-baseline gap-1.5">
                <span className={`text-2xl font-black ${p.isHigh ? 'text-amber-400' : 'text-teal-400'}`}>
                  {p.value}
                </span>
                <span className="text-xs text-slate-400 font-medium">{p.unit}</span>
              </div>

              <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">{p.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
