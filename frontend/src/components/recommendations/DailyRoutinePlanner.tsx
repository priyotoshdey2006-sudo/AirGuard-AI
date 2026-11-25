import React, { useState } from 'react';
import { RoutinePlan, SensitivityLevel } from '../../types';
import { ProvenanceBadge } from '../common/ProvenanceBadge';
import {
  Calendar,
  Sparkles,
  ShieldCheck,
  Plus,
  Trash2,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Flame,
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
      {/* Header Capsule */}
      <div className="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              AI Personalized Daily Routine
            </h1>
            {routine && <ProvenanceBadge provenance={routine.provenance || 'ESTIMATED'} />}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Synchronizes your daily schedule against hourly atmospheric particulate curves to minimize lung intake.
          </p>
        </div>

        {routine && (
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/25 text-xs text-cyan-300 shadow-[inset_0_1px_0_rgba(255,255,255,0.15)]">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>Engine: {routine.model_provider || 'Grounded Clinical AI'}</span>
          </div>
        )}
      </div>

      {/* Activity Input & Generation Controls Card */}
      <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
          <Calendar className="w-3.5 h-3.5 text-emerald-400" />
          <span>Your Scheduled Outdoor Activities for Today</span>
        </h2>

        {/* Activity Pills List */}
        <div className="flex flex-wrap gap-2 mb-4">
          {activities.map((act, index) => (
            <div
              key={index}
              className="flex items-center gap-2 liquid-glass-control rounded-full px-3.5 py-1.5 text-xs text-slate-200"
            >
              <span className="font-medium">{act}</span>
              <button
                onClick={() => handleRemoveActivity(index)}
                className="text-slate-400 hover:text-red-400 transition-colors ml-0.5"
                title="Remove activity"
                aria-label={`Remove activity ${act}`}
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>

        {/* Add Activity Form */}
        <form onSubmit={handleAddActivity} className="flex gap-2.5 mb-5">
          <input
            type="text"
            value={newActivity}
            onChange={(e) => setNewActivity(e.target.value)}
            placeholder="Add outdoor activity (e.g. Football Practice 5 PM, Park Run)..."
            className="flex-1 bg-midnight-950/70 border border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-400/50 shadow-inner"
          />
          <button
            type="submit"
            className="liquid-glass-control flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-200 hover:text-white shrink-0"
          >
            <Plus className="w-3.5 h-3.5 text-emerald-400" />
            <span>Add</span>
          </button>
        </form>

        {/* Main Generate Button */}
        <button
          onClick={() => onGenerate(activities)}
          disabled={loading || activities.length === 0}
          className="w-full relative group overflow-hidden py-3 sm:py-3.5 bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-midnight-950 font-bold text-xs sm:text-sm rounded-2xl shadow-[0_4px_24px_rgba(16,185,129,0.3)] hover:shadow-[0_6px_32px_rgba(16,185,129,0.45)] transition-all duration-300 active:scale-[0.99] disabled:opacity-50"
        >
          <div className="flex items-center justify-center gap-2">
            <Sparkles className={`w-4 h-4 text-midnight-950 ${loading ? 'animate-spin' : ''}`} />
            <span>
              {loading ? 'Evaluating Atmospheric Risk Windows...' : 'Generate Personalized AI Routine'}
            </span>
          </div>
          {/* Specular sheen swipe */}
          <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/30 to-transparent pointer-events-none" />
        </button>
      </div>

      {/* Routine Recommendations Display */}
      {routine && (
        <div className="space-y-6">
          {/* Risk Evaluation Banner */}
          <div className="liquid-glass-card rounded-3xl p-6 sm:p-7 border-l-4 border-l-emerald-400 relative overflow-hidden">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
              <span>Sensitivity Profile: {routine.sensitivity_level}</span>
            </div>
            <h2 className="text-lg sm:text-xl font-bold text-white mt-1.5">
              {routine.overall_risk_assessment}
            </h2>
            <p className="text-sm text-slate-300 mt-2.5 leading-relaxed bg-midnight-950/60 p-4 rounded-2xl border border-white/[0.06] shadow-inner">
              {routine.daily_summary}
            </p>
          </div>

          {/* Activity Window Cards */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 px-1">
              Optimized Activity Timing & Protective Protocols
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {routine.activity_windows.map((win, idx) => {
                const isAvoid = win.safety_rating === 'AVOID';
                const isCaution = win.safety_rating === 'CAUTION';
                return (
                  <div
                    key={idx}
                    className={`liquid-glass-card liquid-glass-hover p-5 sm:p-6 rounded-2xl flex flex-col justify-between ${
                      isAvoid
                        ? 'border-red-500/25 bg-red-500/[0.03]'
                        : isCaution
                        ? 'border-amber-500/25 bg-amber-500/[0.03]'
                        : 'border-emerald-500/25 bg-emerald-500/[0.03]'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-base text-white">{win.activity_name}</span>
                        <span
                          className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider border ${
                            isAvoid
                              ? 'bg-red-500/20 text-red-300 border-red-500/30'
                              : isCaution
                              ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                          }`}
                        >
                          {win.safety_rating}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-xs text-slate-300 my-2.5">
                        <Clock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span className="font-medium">{win.optimal_time}</span>
                        <span className="text-slate-600">•</span>
                        <span className="font-mono text-slate-400">
                          Forecast AQI: <strong className="text-slate-200">{win.expected_aqi}</strong>
                        </span>
                      </div>

                      <div className="bg-midnight-950/70 p-3 rounded-xl border border-white/[0.05] text-xs text-slate-300 mt-2">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Protection Protocol
                        </div>
                        <div className="text-emerald-300 font-semibold mt-0.5">
                          {win.mask_recommendation.replace('_', ' ')}
                        </div>
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 mt-3 leading-relaxed border-t border-white/[0.04] pt-2.5">
                      {win.mitigation_tips}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Items List */}
          <div className="liquid-glass-card rounded-3xl p-6 sm:p-7">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3.5 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Clinical Action Checklist</span>
            </h2>

            <div className="space-y-2.5">
              {routine.action_items.map((item, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 bg-midnight-950/50 p-3.5 rounded-2xl border border-white/[0.05] text-xs text-slate-200"
                >
                  <span className="w-5 h-5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5 tabular-nums">
                    {index + 1}
                  </span>
                  <span className="leading-relaxed">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
