import React from 'react';
import { Activity, CloudSun, Calculator } from 'lucide-react';
import { Provenance } from '../../types';

interface Props {
  provenance: Provenance;
  source?: string;
  timestamp?: string;
  className?: string;
}

export const ProvenanceBadge: React.FC<Props> = ({
  provenance,
  source,
  timestamp,
  className = '',
}) => {
  if (provenance === 'OBSERVED' || provenance === 'MODEL_ANALYSIS') {
    return (
      <span
        title="Atmospheric reanalysis from ECMWF CAMS Global (IFS-AER) model via Open-Meteo (~0.4° spatial grid resolution, not statutory ground CAAQMS sensor telemetry)"
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_12px_rgba(16,185,129,0.15)] ${className}`}
      >
        <Activity className="w-3.5 h-3.5 text-emerald-400" />
        <span className="tracking-wide">ATMOSPHERIC MODEL ANALYSIS</span>
      </span>
    );
  }

  if (provenance === 'FORECAST') {
    return (
      <span
        title="Forward numerical dispersion atmospheric projection from ECMWF CAMS model via Open-Meteo"
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_12px_rgba(6,182,212,0.15)] ${className}`}
      >
        <CloudSun className="w-3.5 h-3.5 text-cyan-400" />
        <span className="tracking-wide">NUMERICAL MODEL FORECAST</span>
      </span>
    );
  }

  return (
    <span
      title="Physical single-zone mass-balance box model estimate based on outdoor atmospheric levels, building infiltration, and CADR filtration"
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-300 border border-purple-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_12px_rgba(168,85,247,0.15)] ${className}`}
    >
      <Calculator className="w-3.5 h-3.5 text-purple-300" />
      <span className="tracking-wide">INDOOR MASS-BALANCE ESTIMATE</span>
    </span>
  );
};
