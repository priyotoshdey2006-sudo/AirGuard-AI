import React, { useState } from 'react';
import { CommunityReport } from '../../types';
import {
  MapPin,
  AlertTriangle,
  Plus,
  ThumbsUp,
  CheckCircle2,
  Clock,
  Filter,
  Flame,
  X,
} from 'lucide-react';

interface Props {
  reports: CommunityReport[];
  loading: boolean;
  userLat: number;
  userLon: number;
  onSubmitReport: (data: {
    title: string;
    description: string;
    category: string;
    severity: number;
    latitude: number;
    longitude: number;
    reporter_name: string;
  }) => void;
  onUpvote: (id: string) => void;
}

export const CommunityHazardMap: React.FC<Props> = ({
  reports,
  loading,
  userLat,
  userLon,
  onSubmitReport,
  onUpvote,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('CONSTRUCTION_DUST');
  const [severity, setSeverity] = useState(3);
  const [reporterName, setReporterName] = useState('Local Citizen');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onSubmitReport({
        title: title.trim(),
        description: description.trim(),
        category,
        severity,
        latitude: userLat,
        longitude: userLon,
        reporter_name: reporterName.trim() || 'Local Citizen',
      });
      setTitle('');
      setDescription('');
      setShowModal(false);
    }
  };

  const filteredReports =
    selectedCategory === 'ALL'
      ? reports
      : reports.filter((r) => r.category === selectedCategory);

  return (
    <div className="space-y-6">
      {/* Header Capsule */}
      <div className="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Crowdsourced Community Hazard Network
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
              CITIZEN SENSING
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time citizen reporting of crop residue burning, industrial smoke plumes, and construction dust.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="relative group overflow-hidden flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-midnight-950 font-bold text-xs rounded-xl shadow-[0_4px_16px_rgba(16,185,129,0.3)] transition-all active:scale-95 shrink-0"
        >
          <Plus className="w-4 h-4 text-midnight-950" />
          <span>Report Pollution Incident</span>
          <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/30 to-transparent pointer-events-none" />
        </button>
      </div>

      {/* Filter Segmented Control */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none text-xs">
        <span className="text-slate-400 flex items-center gap-1 font-semibold pl-1 text-[11px] shrink-0">
          <Filter className="w-3.5 h-3.5 text-emerald-400" />
          <span>Category:</span>
        </span>
        {['ALL', 'STUBBLE_BURNING', 'INDUSTRIAL_EMISSION', 'CONSTRUCTION_DUST', 'GARBAGE_BURNING', 'VEHICULAR_SMOKE'].map(
          (cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl whitespace-nowrap transition-all duration-200 ${
                selectedCategory === cat
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold shadow-[0_0_12px_rgba(16,185,129,0.2)]'
                  : 'liquid-glass-control text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat.replace('_', ' ')}
            </button>
          )
        )}
      </div>

      {/* Incident Cards Grid */}
      <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <span>Active Environmental Incidents ({filteredReports.length})</span>
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">
            Radius: 50km of ({userLat.toFixed(2)}, {userLon.toFixed(2)})
          </span>
        </div>

        {filteredReports.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <CheckCircle2 className="w-10 h-10 text-emerald-500/30 mx-auto mb-2" />
            <p className="text-xs text-slate-400">No active pollution hazard reports in this sector.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="liquid-glass-control liquid-glass-hover p-4 sm:p-5 rounded-2xl flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-white/[0.05] text-emerald-300 border border-white/[0.08]">
                      {report.category.replace('_', ' ')}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        report.status === 'VERIFIED'
                          ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                          : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                      }`}
                    >
                      {report.status}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white">{report.title}</h3>
                  <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                    {report.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-white/[0.05] flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-1.5 text-[11px]">
                    <Clock className="w-3 h-3 text-slate-500" />
                    <span>{new Date(report.created_at).toLocaleDateString()}</span>
                  </div>

                  <button
                    onClick={() => onUpvote(report.id)}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs font-semibold transition-colors border border-emerald-500/20 active:scale-95"
                  >
                    <ThumbsUp className="w-3 h-3" />
                    <span className="tabular-nums">{report.upvotes_count}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Submission Modal Overlay */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-midnight-950/80 backdrop-blur-xl animate-fadeIn">
          <div className="liquid-glass-overlay p-6 sm:p-7 rounded-3xl max-w-lg w-full shadow-2xl relative">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Submit Citizen Pollution Report</span>
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="liquid-glass-control p-1.5 rounded-xl text-slate-400 hover:text-white"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">
                  Incident Headline
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Open trash burning behind wholesale market"
                  className="w-full bg-midnight-950/80 border border-white/[0.08] rounded-xl px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-400/50 shadow-inner"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-midnight-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-400/50"
                  >
                    <option value="CONSTRUCTION_DUST">Construction Dust</option>
                    <option value="STUBBLE_BURNING">Stubble / Biomass Burning</option>
                    <option value="INDUSTRIAL_EMISSION">Industrial Emission</option>
                    <option value="GARBAGE_BURNING">Garbage Burning</option>
                    <option value="VEHICULAR_SMOKE">Heavy Vehicular Smoke</option>
                    <option value="OTHER">Other Hazard</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Severity (1 to 5)</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(Number(e.target.value))}
                    className="w-full bg-midnight-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-400/50"
                  >
                    <option value={1}>1 - Low Odor / Mild</option>
                    <option value={2}>2 - Moderate</option>
                    <option value={3}>3 - Significant Smog</option>
                    <option value={4}>4 - Dense Choking Plume</option>
                    <option value={5}>5 - Hazardous Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">
                  Detailed Description
                </label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe location landmarks, visible smoke color, or wind drift..."
                  className="w-full bg-midnight-950/80 border border-white/[0.08] rounded-xl px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-400/50 shadow-inner"
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="liquid-glass-control px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-midnight-950 text-xs font-bold rounded-xl transition-all shadow-[0_4px_16px_rgba(16,185,129,0.3)]"
                >
                  Publish Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
