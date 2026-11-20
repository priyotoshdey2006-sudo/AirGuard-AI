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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">Sustainable Transit & Respiratory Impact</h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
              MULTI-MODAL ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Compares inhaled pollutant intake against net carbon dioxide emissions across transit options.
          </p>
        </div>
      </div>

      {/* Commute Route Form */}
      <div className="glass-panel p-6 rounded-2xl">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Origin Point</label>
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Destination Point</label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-xs rounded-lg transition-colors shadow-md disabled:opacity-50"
            >
              {loading ? 'Evaluating Transit...' : 'Compare Transit Alternatives'}
            </button>
          </div>
        </form>
      </div>

      {comparison && (
        <div className="space-y-6">
          {/* Summary Impact Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-panel p-5 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 uppercase font-bold">Estimated Distance</span>
              <div className="text-3xl font-black text-slate-100 mt-2">{comparison.distance_km} km</div>
              <div className="text-xs text-slate-500 mt-1">Urban transit corridor</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-teal-500/30 bg-teal-500/5">
              <span className="text-xs text-teal-400 uppercase font-bold">Cleanest Air Transit</span>
              <div className="text-3xl font-black text-teal-300 mt-2">{comparison.cleanest_mode}</div>
              <div className="text-xs text-slate-300 mt-1">Lowest inhaled particulate exposure</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/5">
              <span className="text-xs text-emerald-400 uppercase font-bold">Max Carbon Savings</span>
              <div className="text-3xl font-black text-emerald-300 mt-2 flex items-center gap-2">
                <TreePine className="w-6 h-6 text-emerald-400" />
                <span>{comparison.total_trees_equivalent} Trees/yr</span>
              </div>
              <div className="text-xs text-slate-300 mt-1">Equivalent carbon offset per trip</div>
            </div>
          </div>

          {/* Transit Alternatives Table */}
          <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Navigation className="w-4 h-4 text-teal-400" />
                <span>Transit Mode Comparison & Inhaled Particulate Intake</span>
              </h3>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/80 text-slate-400 uppercase text-[11px] font-bold border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Mode</th>
                    <th className="py-3 px-4">Duration</th>
                    <th className="py-3 px-4">CO2 Footprint</th>
                    <th className="py-3 px-4">Net CO2 Saved</th>
                    <th className="py-3 px-4">Inhaled Exposure</th>
                    <th className="py-3 px-4">Clinical Recommendation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {comparison.options.map((opt, idx) => (
                    <tr
                      key={idx}
                      className={`hover:bg-slate-800/30 transition-colors ${
                        opt.recommended ? 'bg-teal-500/5' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4 font-bold text-slate-100 flex items-center gap-2">
                        {opt.recommended && <ShieldCheck className="w-4 h-4 text-teal-400 shrink-0" />}
                        <span>{opt.mode_label}</span>
                      </td>
                      <td className="py-3.5 px-4 font-mono">{opt.duration_minutes} min</td>
                      <td className="py-3.5 px-4 font-mono">{opt.co2_kg} kg</td>
                      <td className="py-3.5 px-4 font-mono text-emerald-400 font-bold">
                        {opt.co2_saved_kg > 0 ? `+${opt.co2_saved_kg} kg` : '0 kg (Baseline)'}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            opt.exposure_level === 'LOW'
                              ? 'bg-emerald-500/20 text-emerald-300'
                              : opt.exposure_level === 'MODERATE'
                              ? 'bg-amber-500/20 text-amber-300'
                              : 'bg-red-500/20 text-red-300'
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
