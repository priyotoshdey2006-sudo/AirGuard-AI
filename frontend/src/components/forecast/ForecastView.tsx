import React from 'react';
import { ForecastData } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { Clock, TrendingUp, Sparkles, Sun } from 'lucide-react';

interface Props {
  forecast: ForecastData | null;
  loading: boolean;
}

export const ForecastView: React.FC<Props> = ({ forecast, loading }) => {
  if (loading && !forecast) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[350px] text-slate-400 gap-3">
        <div className="w-10 h-10 border-4 border-teal-500/20 border-t-teal-400 rounded-full animate-spin" />
        <p className="text-sm font-medium">Computing atmospheric forecast models...</p>
      </div>
    );
  }

  if (!forecast) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center max-w-md mx-auto my-12">
        <Clock className="w-12 h-12 text-slate-500 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-200">No Forecast Data Available</h3>
        <p className="text-xs text-slate-400 mt-1">Select a location to load 24-hour atmospheric projections.</p>
      </div>
    );
  }

  // Format hourly chart data
  const chartData = forecast.hourly.map((item) => {
    const hour = item.time.includes('T') ? item.time.split('T')[1].substring(0, 5) : item.time;
    return {
      hour,
      AQI: item.aqi_us,
      'PM2.5': item.pm2_5,
      'PM10': item.pm10,
      category: item.category,
    };
  });

  // Calculate clean window
  const minAQIItem = [...forecast.hourly].sort((a, b) => a.aqi_us - b.aqi_us)[0];
  const maxAQIItem = [...forecast.hourly].sort((a, b) => b.aqi_us - a.aqi_us)[0];

  return (
    <div className="space-y-6">
      {/* Forecast Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">24-Hour Diurnal Pollution Curve</h2>
            <ProvenanceBadge provenance={forecast.provenance} />
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Atmospheric dispersion trajectory showing nocturnal inversion peaks and daytime convection clearing.
          </p>
        </div>

        {minAQIItem && (
          <div className="flex items-center gap-2 bg-teal-500/10 border border-teal-500/20 px-3 py-1.5 rounded-lg text-xs text-teal-300">
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>
              Cleanest Air Window:{' '}
              <strong className="text-teal-200 font-bold">
                {minAQIItem.time.split('T')[1]?.substring(0, 5) || minAQIItem.time} (AQI {minAQIItem.aqi_us})
              </strong>
            </span>
          </div>
        )}
      </div>

      {/* Hourly Area Chart */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              Hourly US AQI & Particulate Infiltration Trend
            </h3>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-teal-400">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-400" />
              <span>AQI (0-500)</span>
            </div>
            <div className="flex items-center gap-1.5 text-cyan-400">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
              <span>PM2.5 (µg/m³)</span>
            </div>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="pm25Gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="hour" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.75rem',
                  fontSize: '0.75rem',
                }}
              />
              <Area
                type="monotone"
                dataKey="AQI"
                stroke="#14b8a6"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#aqiGradient)"
              />
              <Area
                type="monotone"
                dataKey="PM2.5"
                stroke="#06b6d4"
                strokeWidth={1.5}
                fillOpacity={1}
                fill="url(#pm25Gradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 7-Day Projection Summary */}
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center gap-2">
          <Sun className="w-4 h-4 text-amber-400" />
          <span>7-Day Synoptic Air Quality Projections</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
          {forecast.daily.map((d, idx) => (
            <div
              key={idx}
              className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-center hover:border-slate-700 transition-colors"
            >
              <div className="text-xs font-semibold text-slate-400">{d.date}</div>
              <div className="text-xl font-black text-slate-100 my-1">{d.max_aqi}</div>
              <div className="text-[10px] text-slate-400">Min: {d.min_aqi}</div>
              <div className="mt-2 text-[10px] px-2 py-0.5 rounded-full font-medium bg-slate-800 text-slate-300 truncate">
                {d.category}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
