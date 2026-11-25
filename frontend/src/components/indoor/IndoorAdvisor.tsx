import React, { useState } from 'react';
import { IndoorGuidance } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import { Home, Wind, ShieldCheck, Clock, Settings, Sparkles, Filter, CheckCircle2 } from 'lucide-react';

interface Props {
  guidance: IndoorGuidance | null;
  loading: boolean;
  onCalculate: (roomSqft: number, hasHepa: boolean) => void;
}

export const IndoorAdvisor: React.FC<Props> = ({ guidance, loading, onCalculate }) => {
  const [roomSqft, setRoomSqft] = useState(400);
  const [hasHepa, setHasHepa] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCalculate(roomSqft, hasHepa);
  };

  const reductionPercent =
    guidance && guidance.outdoor_aqi > 0
      ? Math.round(
          ((guidance.outdoor_aqi - guidance.estimated_indoor_aqi) / guidance.outdoor_aqi) * 100
        )
      : null;

  return (
    <div className="space-y-6">
      {/* Header Capsule */}
      <div className="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Indoor Air Quality & Ventilation Advisor
            </h1>
            {guidance && <ProvenanceBadge provenance={guidance.provenance || 'ESTIMATED'} />}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Physical single-zone mass-balance box model calculating particulate infiltration, window ventilation windows, and CADR.
          </p>
        </div>
      </div>

      {/* Building & Room Parameters Form */}
      <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center gap-2">
          <Settings className="w-3.5 h-3.5 text-emerald-400" />
          <span>Indoor Envelope & Filtration Parameters</span>
        </h2>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Room Surface Area (sq ft)
            </label>
            <input
              type="number"
              min={50}
              max={5000}
              value={roomSqft}
              onChange={(e) => setRoomSqft(Number(e.target.value))}
              className="w-full bg-midnight-950/70 border border-white/[0.08] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-400/50 shadow-inner"
            />
          </div>

          <div className="flex flex-col justify-end">
            <label className="flex items-center gap-2.5 cursor-pointer liquid-glass-control rounded-xl px-3.5 py-2 text-xs text-slate-200 select-none">
              <input
                type="checkbox"
                checked={hasHepa}
                onChange={(e) => setHasHepa(e.target.checked)}
                className="rounded border-slate-700 text-emerald-500 focus:ring-emerald-400/30 accent-emerald-500 w-4 h-4 cursor-pointer"
              />
              <span className="font-medium">Active True HEPA Air Purifier</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-midnight-950 font-bold text-xs rounded-xl shadow-[0_4px_16px_rgba(16,185,129,0.25)] transition-all active:scale-[0.99] disabled:opacity-50"
            >
              {loading ? 'Recalculating Mass-Balance...' : 'Update Indoor Advisory'}
            </button>
          </div>
        </form>
      </div>

      {guidance && (
        <div className="space-y-6">
          {/* Outdoor vs Indoor Comparison Deck */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Outdoor Ambient Card */}
            <div className="liquid-glass-card rounded-3xl p-6 sm:p-7 text-center relative overflow-hidden">
              <span className="text-xs uppercase font-bold tracking-wider text-slate-400">
                Outdoor Ambient Particulate
              </span>
              <div className="text-5xl sm:text-6xl font-black text-amber-400 tabular-nums my-4">
                {guidance.outdoor_aqi}
              </div>
              <div className="text-xs text-slate-400 font-medium">
                Current external atmospheric concentration
              </div>
            </div>

            {/* Indoor Estimated Card with Reduction Badge */}
            <div className="liquid-glass-card rounded-3xl p-6 sm:p-7 text-center border-emerald-500/25 relative overflow-hidden">
              {reductionPercent != null && reductionPercent > 0 && (
                <div className="absolute top-4 right-4 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                  ↓ {reductionPercent}% Lower Infiltration
                </div>
              )}
              <span className="text-xs uppercase font-bold tracking-wider text-emerald-400">
                Estimated Indoor Air Quality
              </span>
              <div className="text-5xl sm:text-6xl font-black text-emerald-300 tabular-nums my-4">
                {guidance.estimated_indoor_aqi}
              </div>
              <div className="text-xs text-slate-200 font-semibold uppercase tracking-wider">
                {guidance.indoor_category}
              </div>
            </div>
          </div>

          {/* Window Ventilation & Purifier Guidance Card */}
          <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Wind className="w-3.5 h-3.5" />
              </div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Window Ventilation & HEPA Filtration Protocols
              </h2>
            </div>

            <div className="bg-midnight-950/60 p-4 rounded-2xl border border-white/[0.06] text-sm text-slate-200 mb-5 leading-relaxed shadow-inner">
              {guidance.window_advice}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="liquid-glass-control p-4 rounded-2xl">
                <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                  Purifier Runtime Recommendation
                </div>
                <div className="text-2xl font-bold text-white tabular-nums mt-1">
                  {guidance.hepa_runtime_recommendation_hours} hrs / day
                </div>
              </div>

              <div className="liquid-glass-control p-4 rounded-2xl">
                <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                  Recommended Fan Speed
                </div>
                <div className="text-2xl font-bold text-emerald-400 mt-1">
                  {guidance.air_cleaner_speed}
                </div>
              </div>
            </div>

            {/* Safe Natural Airflow Windows */}
            {guidance.safe_ventilation_windows && guidance.safe_ventilation_windows.length > 0 && (
              <div className="mt-5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">
                  Safe Natural Airflow Windows
                </h3>
                <div className="space-y-2">
                  {guidance.safe_ventilation_windows.map((win, idx) => (
                    <div
                      key={idx}
                      className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-2xl bg-emerald-500/[0.08] border border-emerald-500/20 text-xs text-emerald-200"
                    >
                      <div className="flex items-center gap-2">
                        <Clock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span className="font-bold tabular-nums">
                          {win.start_time} - {win.end_time}
                        </span>
                      </div>
                      <span className="text-emerald-300 text-[11px] sm:text-xs">
                        {win.recommendation}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Practical Indoor Protocols */}
          <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3.5 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Indoor Health & Deposition Protocols</span>
            </h2>

            <div className="space-y-2.5">
              {guidance.tips.map((tip, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 bg-midnight-950/50 p-3.5 rounded-2xl border border-white/[0.05] text-xs text-slate-200"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
