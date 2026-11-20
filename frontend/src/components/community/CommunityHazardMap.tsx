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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">Crowdsourced Community Hazard Network</h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
              CITIZEN SENSING
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time community reporting of local crop burning, industrial plumes, and construction dust.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-xs rounded-xl shadow-md transition-all active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>Report Pollution Incident</span>
        </button>
      </div>

      {/* Filter Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none text-xs">
        <span className="text-slate-400 flex items-center gap-1 font-semibold pl-1">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter:</span>
        </span>
        {['ALL', 'STUBBLE_BURNING', 'INDUSTRIAL_EMISSION', 'CONSTRUCTION_DUST', 'GARBAGE_BURNING', 'VEHICULAR_SMOKE'].map(
          (cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40 font-bold'
                  : 'bg-slate-900/60 text-slate-400 hover:bg-slate-800 border border-slate-800'
              }`}
            >
              {cat.replace('_', ' ')}
            </button>
          )
        )}
      </div>

      {/* Interactive Spatial Grid / Map Representation */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-teal-400" />
            <span>Active Environmental Incidents ({filteredReports.length})</span>
          </h3>
          <span className="text-xs text-slate-500 font-mono">
            Radius: 50km of ({userLat.toFixed(2)}, {userLon.toFixed(2)})
          </span>
        </div>

        {filteredReports.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <CheckCircle2 className="w-10 h-10 text-teal-500/40 mx-auto mb-2" />
            <p className="text-xs">No active pollution hazard reports in this sector.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="bg-slate-900/70 p-4 rounded-xl border border-slate-800/90 hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-teal-300 border border-slate-700">
                      {report.category.replace('_', ' ')}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        report.status === 'VERIFIED'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}
                    >
                      {report.status}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-100">{report.title}</h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">{report.description}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-1.5 text-[11px]">
                    <Clock className="w-3 h-3 text-slate-500" />
                    <span>{new Date(report.created_at).toLocaleDateString()}</span>
                  </div>

                  <button
                    onClick={() => onUpvote(report.id)}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 text-xs font-semibold transition-colors border border-teal-500/20"
                  >
                    <ThumbsUp className="w-3 h-3" />
                    <span>{report.upvotes_count}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Submission Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-lg w-full border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Submit Citizen Pollution Report</span>
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Incident Headline</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Open trash burning behind market"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
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
                  <label className="block text-xs font-medium text-slate-400 mb-1">Severity (1 to 5)</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(Number(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
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
                <label className="block text-xs font-medium text-slate-400 mb-1">Detailed Description</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe location landmarks, visible smoke color, or wind drift..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition-all"
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
