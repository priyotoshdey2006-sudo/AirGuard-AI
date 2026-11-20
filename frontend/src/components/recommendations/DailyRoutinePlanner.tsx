import React, { useState } from 'react';
import { RoutinePlan, SensitivityLevel } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import {
  Calendar,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Plus,
  Trash2,
  Clock,
  CheckCircle,
} from 'lucide-react';

interface Props {
  routine: RoutinePlan | null;
  loading: boolean;
  sensitivity: SensitivityLevel;
  onGenerate: (activities: string[]) => void;
}

export const DailyRoutinePlanner: React.FC<Props> = ({
  routine,
  loading,
  sensitivity,
  onGenerate,
}) => {
  const [activities, setActivities] = useState<string[]>([
    'Morning Jog (07:00)',
    'Commute to Office (09:00)',
    'Outdoor Lunch Walk (13:00)',
    'Evening Commute (18:30)',
  ]);
  const [newActivity, setNewActivity] = useState('');

  const handleAddActivity = (e: React.FormEvent) => {
    e.preventDefault();
    if (newActivity.trim()) {
      setActivities([...activities, newActivity.trim()]);
      setNewActivity('');
    }
  };

  const handleRemoveActivity = (index: number) => {
    setActivities(activities.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">AI Personalized Daily Routine</h2>
            {routine && <ProvenanceBadge provenance={routine.provenance} />}
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Synchronizes your daily outdoor schedule with hourly atmospheric dispersion forecasts.
          </p>
        </div>

        {routine && (
          <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-500/10 border border-purple-500/20 text-purple-300 rounded-lg text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>Powered by: {routine.model_provider}</span>
          </div>
        )}
      </div>

      {/* Activity Input & Generation Controls */}
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-teal-400" />
          <span>Your Planned Activities for Today</span>
        </h3>

        <div className="flex flex-wrap gap-2 mb-4">
          {activities.map((act, index) => (
            <div
              key={index}
              className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/80 px-3 py-1.5 rounded-lg text-xs text-slate-200"
            >
              <span>{act}</span>
              <button
                onClick={() => handleRemoveActivity(index)}
                className="text-slate-500 hover:text-red-400 transition-colors"
                title="Remove activity"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>

        <form onSubmit={handleAddActivity} className="flex gap-2 mb-4">
          <input
            type="text"
            value={newActivity}
            onChange={(e) => setNewActivity(e.target.value)}
            placeholder="Add activity (e.g. Outdoor Football 5 PM)..."
            className="flex-1 bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500"
          />
          <button
            type="submit"
            className="flex items-center gap-1 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors border border-slate-700"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add</span>
          </button>
        </form>

        <button
          onClick={() => onGenerate(activities)}
          disabled={loading || activities.length === 0}
          className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-sm rounded-xl shadow-lg transition-all active:scale-[0.99] disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Evaluating Environmental Risks...' : 'Generate Personalized AI Routine'}</span>
        </button>
      </div>

      {/* Routine Output Display */}
      {routine && (
        <div className="space-y-6">
          {/* Clinical Risk Banner */}
          <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-teal-400">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-400">
              <ShieldCheck className="w-4 h-4" />
              <span>Assessment Profile: {routine.sensitivity_level}</span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 mt-1">{routine.overall_risk_assessment}</h3>
            <p className="text-sm text-slate-300 mt-2 leading-relaxed bg-slate-900/40 p-4 rounded-xl border border-slate-800/80">
              {routine.daily_summary}
            </p>
          </div>

          {/* Activity Timeline Cards */}
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3">
              Optimized Activity Timing & Protective Protocols
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {routine.activity_windows.map((win, idx) => {
                const isAvoid = win.safety_rating === 'AVOID';
                const isCaution = win.safety_rating === 'CAUTION';
                return (
                  <div
                    key={idx}
                    className={`glass-panel p-5 rounded-2xl border transition-all ${
                      isAvoid
                        ? 'border-red-500/30 bg-red-500/5'
                        : isCaution
                        ? 'border-amber-500/30 bg-amber-500/5'
                        : 'border-emerald-500/30 bg-emerald-500/5'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-base text-slate-100">{win.activity_name}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          isAvoid
                            ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                            : isCaution
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        }`}
                      >
                        {win.safety_rating}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-slate-300 my-2">
                      <Clock className="w-3.5 h-3.5 text-teal-400" />
                      <span>{win.optimal_time}</span>
                      <span className="text-slate-500">•</span>
                      <span>Expected AQI: {win.expected_aqi}</span>
                    </div>

                    <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-xs text-slate-300 mt-2">
                      <div className="text-[11px] font-bold text-slate-400 uppercase">Mask Advice</div>
                      <div className="text-teal-300 font-semibold">{win.mask_recommendation.replace('_', ' ')}</div>
                    </div>

                    <p className="text-xs text-slate-400 mt-3 leading-relaxed">{win.mitigation_tips}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Items List */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Recommended Daily Action Checklist</span>
            </h3>

            <div className="space-y-2">
              {routine.action_items.map((item, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2.5 bg-slate-900/40 p-3 rounded-xl border border-slate-800/80 text-xs text-slate-300"
                >
                  <span className="w-4 h-4 rounded-full bg-teal-500/20 text-teal-300 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                    {index + 1}
                  </span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
