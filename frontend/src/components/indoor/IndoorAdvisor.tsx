import React, { useState } from 'react';
import { IndoorGuidance } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import { Home, Wind, ShieldCheck, Clock, Settings, Sparkles, AlertCircle } from 'lucide-react';

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">Indoor Air Quality & Ventilation Advisor</h2>
            {guidance && <ProvenanceBadge provenance={guidance.provenance} />}
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Micro-climate estimation model calculating indoor particulate penetration, ventilation windows, and CADR.
          </p>
        </div>
      </div>

      {/* Building & Room Parameters Form */}
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
          <Settings className="w-4 h-4 text-teal-400" />
          <span>Home / Room Parameters</span>
        </h3>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Room Area (sq ft)</label>
            <input
              type="number"
              min={50}
              max={5000}
              value={roomSqft}
              onChange={(e) => setRoomSqft(Number(e.target.value))}
              className="w-full bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
            />
          </div>

          <div className="flex flex-col justify-end">
            <label className="flex items-center gap-2 cursor-pointer bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200">
              <input
                type="checkbox"
                checked={hasHepa}
                onChange={(e) => setHasHepa(e.target.checked)}
                className="rounded border-slate-700 text-teal-500 focus:ring-teal-500/20"
              />
              <span>Equipped with HEPA Purifier</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? 'Recalculating...' : 'Update Indoor Advisory'}
            </button>
          </div>
        </form>
      </div>

      {guidance && (
        <div className="space-y-6">
          {/* Outdoor vs Indoor Comparison Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 text-center">
              <span className="text-xs uppercase font-bold tracking-wider text-slate-400">Outdoor Ambient Air</span>
              <div className="text-5xl font-black text-amber-400 my-4">{guidance.outdoor_aqi}</div>
              <div className="text-xs text-slate-400">Current ambient sensor concentration</div>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-teal-500/30 bg-teal-500/5 text-center">
              <span className="text-xs uppercase font-bold tracking-wider text-teal-400">
                Estimated Indoor Air Quality
              </span>
              <div className="text-5xl font-black text-teal-300 my-4">{guidance.estimated_indoor_aqi}</div>
              <div className="text-xs text-slate-300 font-semibold">{guidance.indoor_category}</div>
            </div>
          </div>

          {/* Window Ventilation Guidance */}
          <div className="glass-panel p-6 rounded-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Wind className="w-4 h-4 text-teal-400" />
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                Window Ventilation & Air Purifier Plan
              </h3>
            </div>

            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 text-sm text-slate-200 mb-4 leading-relaxed">
              {guidance.window_advice}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400 uppercase font-bold">HEPA Recommended Runtime</div>
                <div className="text-2xl font-bold text-slate-100 mt-1">
                  {guidance.hepa_runtime_recommendation_hours} hrs / day
                </div>
              </div>

              <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400 uppercase font-bold">Recommended Fan Speed</div>
                <div className="text-2xl font-bold text-teal-400 mt-1">{guidance.air_cleaner_speed}</div>
              </div>
            </div>

            {guidance.safe_ventilation_windows.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Safe Natural Airflow Windows
                </h4>
                {guidance.safe_ventilation_windows.map((win, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between bg-teal-500/10 border border-teal-500/20 p-3 rounded-xl text-xs text-teal-200"
                  >
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-teal-400" />
                      <span className="font-bold">
                        {win.start_time} - {win.end_time}
                      </span>
                    </div>
                    <span className="text-teal-300">{win.recommendation}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Practical Indoor Mitigation Tips */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Indoor Environmental Protocols</span>
            </h3>

            <div className="space-y-2">
              {guidance.tips.map((tip, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2.5 bg-slate-900/40 p-3 rounded-xl border border-slate-800 text-xs text-slate-300"
                >
                  <Sparkles className="w-3.5 h-3.5 text-teal-400 shrink-0 mt-0.5" />
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
