import React from 'react';
import { ForecastData, HourlyForecast } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Clock, TrendingUp, Sparkles, Sun, Calendar } from 'lucide-react';

interface Props {
  forecast: ForecastData | null;
  loading: boolean;
}

export const ForecastView: React.FC<Props> = ({ forecast, loading }) => {
  if (loading && !forecast) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[380px] text-slate-400 gap-4">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 rounded-full border-2 border-emerald-500/20" />
          <div className="absolute inset-0 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
        </div>
        <p className="text-xs font-semibold tracking-wide uppercase text-slate-400 animate-pulse">
          Computing Atmospheric Dispersion Models...
        </p>
      </div>
    );
  }

  if (!forecast) {
    return (
      <div className="liquid-glass-card p-8 rounded-3xl text-center max-w-md mx-auto my-12 border border-white/[0.08]">
        <Clock className="w-12 h-12 text-slate-500 mx-auto mb-3" />
        <h3 className="text-base font-bold text-white">No Forecast Telemetry Available</h3>
        <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
          Select a geographic coordinate or target city to load 24-hour diurnal atmospheric curves.
        </p>
      </div>
    );
  }

  const hourlyList: HourlyForecast[] = Array.isArray(forecast.hourly)
    ? forecast.hourly
    : Array.isArray((forecast as any).forecast_series)
    ? (forecast as any).forecast_series.map((item: any) => ({
        time: item.time_local || item.time_utc || item.time || '',
        aqi_us: item.us_proxy_index ?? item.cpcb_proxy_index ?? item.aqi_us ?? 0,
        pm2_5: item.pm2_5 ?? 0,
        pm10: item.pm10 ?? 0,
        category: item.category || 'Moderate',
      }))
    : [];

  // Format hourly chart data
  const chartData = hourlyList.map((item: HourlyForecast) => {
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
  const minAQIItem = hourlyList.length > 0 ? [...hourlyList].sort((a, b) => a.aqi_us - b.aqi_us)[0] : null;

  return (
    <div className="space-y-6">
      {/* Header Capsule */}
      <div className="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              24-Hour Diurnal Pollution Curve
            </h1>
            <ProvenanceBadge provenance={forecast.provenance || 'FORECAST'} />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Atmospheric dispersion trajectory showing nocturnal inversion peaks and daytime solar convection clearance.
          </p>
        </div>

        {minAQIItem && (
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-xs text-emerald-300 shadow-[inset_0_1px_0_rgba(255,255,255,0.15)]">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>
              Clean Air Window:{' '}
              <strong className="text-white font-bold tabular-nums">
                {minAQIItem.time.split('T')[1]?.substring(0, 5) || minAQIItem.time} (AQI {minAQIItem.aqi_us})
              </strong>
            </span>
          </div>
        )}
      </div>

      {/* Hourly Area Chart Card */}
      <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <TrendingUp className="w-3.5 h-3.5" />
            </div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Hourly US AQI & Particulate Concentration Trajectory
            </h2>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
              <span className="font-medium">AQI Index</span>
            </div>
            <div className="flex items-center gap-1.5 text-cyan-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
              <span className="font-medium">PM2.5 (µg/m³)</span>
            </div>
          </div>
        </div>

        <div className="h-72 sm:h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="aqiLiquidGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="pm25LiquidGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
              <XAxis
                dataKey="hour"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(9, 16, 33, 0.92)',
                  backdropFilter: 'blur(16px)',
                  WebkitBackdropFilter: 'blur(16px)',
                  borderColor: 'rgba(255, 255, 255, 0.12)',
                  borderRadius: '1rem',
                  fontSize: '0.75rem',
                  color: '#f8fafc',
                  boxShadow: '0 12px 32px rgba(0,0,0,0.6)',
                }}
              />
              <Area
                type="monotone"
                dataKey="AQI"
                stroke="#10b981"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#aqiLiquidGradient)"
              />
              <Area
                type="monotone"
                dataKey="PM2.5"
                stroke="#06b6d4"
                strokeWidth={1.5}
                fillOpacity={1}
                fill="url(#pm25LiquidGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 7-Day Synoptic Projection Grid */}
      <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center gap-2">
          <Sun className="w-3.5 h-3.5 text-amber-400" />
          <span>7-Day Atmospheric Dispersion Outlook</span>
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
          {(forecast.daily || []).map((d, idx) => (
            <div
              key={idx}
              className="liquid-glass-control p-3.5 rounded-2xl text-center flex flex-col justify-between hover:border-emerald-500/30 transition-all duration-300"
            >
              <div className="text-xs font-semibold text-slate-300">{d.date}</div>
              <div className="text-2xl font-black text-white tabular-nums my-2">
                {d.max_aqi}
              </div>
              <div className="text-[11px] text-slate-400 font-mono">Min: {d.min_aqi}</div>
              <div className="mt-2.5 text-[10px] px-2 py-0.5 rounded-full font-medium bg-white/[0.05] text-slate-300 border border-white/[0.06] truncate">
                {d.category}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
