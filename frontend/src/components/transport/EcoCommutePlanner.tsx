import React, { useState } from 'react';
import { RouteComparison } from '../../types';
import { Navigation, Leaf, Wind, CheckCircle2, TreePine, ArrowRight, ShieldCheck } from 'lucide-react';

interface Props {
  comparison: RouteComparison | null;
  loading: boolean;
  onCompare: (origin: string, destination: string) => void;
}

export const EcoCommutePlanner: React.FC<Props> = ({ comparison, loading, onCompare }) => {
  const [origin, setOrigin] = useState('Central Connaught Place');
  const [destination, setDestination] = useState('Noida Cyber City');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (origin.trim() && destination.trim()) {
      onCompare(origin.trim(), destination.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Capsule */}
      <div className="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Sustainable Transit & Respiratory Impact
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              MULTI-MODAL ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Compares inhaled pollutant particulate volume against net carbon emissions across urban transit alternatives.
          </p>
        </div>
      </div>

      {/* Commute Route Form */}
      <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Origin Point</label>
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full bg-midnight-950/70 border border-white/[0.08] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-400/50 shadow-inner"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Destination Point</label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full bg-midnight-950/70 border border-white/[0.08] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-400/50 shadow-inner"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-midnight-950 font-bold text-xs rounded-xl shadow-[0_4px_16px_rgba(16,185,129,0.25)] transition-all active:scale-[0.99] disabled:opacity-50"
            >
              {loading ? 'Evaluating Transit Options...' : 'Compare Transit Alternatives'}
            </button>
          </div>
        </form>
      </div>

      {comparison && (
        <div className="space-y-6">
          {/* Summary Impact Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="liquid-glass-card p-5 sm:p-6 rounded-2xl">
              <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">
                Corridor Distance
              </span>
              <div className="text-3xl font-black text-white tabular-nums mt-2">
                {comparison.distance_km} km
              </div>
              <div className="text-xs text-slate-400 mt-1">Urban multi-modal route</div>
            </div>

            <div className="liquid-glass-card p-5 sm:p-6 rounded-2xl border-cyan-500/25">
              <span className="text-xs text-cyan-400 uppercase font-bold tracking-wider">
                Cleanest Air Transit
              </span>
              <div className="text-3xl font-black text-cyan-300 mt-2">
                {comparison.cleanest_mode}
              </div>
              <div className="text-xs text-slate-300 mt-1">Lowest inhaled particulate volume</div>
            </div>

            <div className="liquid-glass-card p-5 sm:p-6 rounded-2xl border-emerald-500/25">
              <span className="text-xs text-emerald-400 uppercase font-bold tracking-wider">
                Max Carbon Offset
              </span>
              <div className="text-3xl font-black text-emerald-300 mt-2 flex items-center gap-2">
                <TreePine className="w-6 h-6 text-emerald-400 shrink-0" />
                <span className="tabular-nums">{comparison.total_trees_equivalent} Trees/yr</span>
              </div>
              <div className="text-xs text-slate-300 mt-1">Equivalent annual absorption factor</div>
            </div>
          </div>

          {/* Transit Alternatives Table */}
          <div className="liquid-glass-card rounded-3xl overflow-hidden">
            <div className="p-4 sm:p-5 border-b border-white/[0.06] flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Navigation className="w-3.5 h-3.5 text-emerald-400" />
                <span>Modal Breakdown: Carbon Emissions & Respiratory Inhalation Intake</span>
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-200">
                <thead className="bg-midnight-950/60 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-white/[0.06]">
                  <tr>
                    <th className="py-3 px-4">Transit Mode</th>
                    <th className="py-3 px-4">Duration</th>
                    <th className="py-3 px-4">CO2 Footprint</th>
                    <th className="py-3 px-4">Net CO2 Saved</th>
                    <th className="py-3 px-4">Inhaled Exposure</th>
                    <th className="py-3 px-4">Clinical Recommendation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04]">
                  {comparison.options.map((opt, idx) => (
                    <tr
                      key={idx}
                      className={`hover:bg-white/[0.02] transition-colors ${
                        opt.recommended ? 'bg-emerald-500/[0.04]' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4 font-bold text-white flex items-center gap-2">
                        {opt.recommended && <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />}
                        <span>{opt.mode_label}</span>
                      </td>
                      <td className="py-3.5 px-4 font-mono tabular-nums">{opt.duration_minutes} min</td>
                      <td className="py-3.5 px-4 font-mono tabular-nums">{opt.co2_kg} kg</td>
                      <td className="py-3.5 px-4 font-mono tabular-nums text-emerald-400 font-bold">
                        {opt.co2_saved_kg > 0 ? `+${opt.co2_saved_kg} kg` : '0 kg (Baseline)'}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border tabular-nums ${
                            opt.exposure_level === 'LOW'
                              ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                              : opt.exposure_level === 'MODERATE'
                              ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                              : 'bg-red-500/15 text-red-300 border-red-500/30'
                          }`}
                        >
                          {opt.exposure_level} ({opt.aqi_exposure_score})
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                        {opt.recommendation_reason || (opt.co2_saved_kg > 0 ? 'Good green alternative' : 'High emissions')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
