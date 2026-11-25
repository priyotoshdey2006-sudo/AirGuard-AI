import React from 'react';
import { ShieldCheck, CloudSun, Calculator } from 'lucide-react';
import { Provenance } from '../../types';

interface Props {
  provenance: Provenance;
  className?: string;
}

export const ProvenanceBadge: React.FC<Props> = ({ provenance, className = '' }) => {
  if (provenance === 'OBSERVED') {
    return (
      <span
        title="Direct measurement from verified satellite or ground monitoring stations"
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_12px_rgba(16,185,129,0.15)] ${className}`}
      >
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span className="tracking-wide">OBSERVED DATA</span>
      </span>
    );
  }

  if (provenance === 'FORECAST') {
    return (
      <span
        title="Numerical atmospheric dispersion model projection"
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_12px_rgba(6,182,212,0.15)] ${className}`}
      >
        <CloudSun className="w-3.5 h-3.5 text-cyan-400" />
        <span className="tracking-wide">FORECAST MODEL</span>
      </span>
    );
  }

  return (
    <span
      title="Estimated based on indoor building envelope and micro-climate filtration physics"
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-300 border border-purple-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.1),0_0_12px_rgba(168,85,247,0.15)] ${className}`}
    >
      <Calculator className="w-3.5 h-3.5 text-purple-300" />
      <span className="tracking-wide">PHYSICAL ESTIMATE</span>
    </span>
  );
};
