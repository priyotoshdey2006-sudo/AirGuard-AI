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
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${className}`}
      >
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>OBSERVED DATA</span>
      </span>
    );
  }

  if (provenance === 'FORECAST') {
    return (
      <span
        title="Numerical atmospheric dispersion model projection"
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 ${className}`}
      >
        <CloudSun className="w-3.5 h-3.5 text-cyan-400" />
        <span>FORECAST MODEL</span>
      </span>
    );
  }

  return (
    <span
      title="Estimated based on indoor building envelope and micro-climate filtration physics"
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20 ${className}`}
    >
      <Calculator className="w-3.5 h-3.5 text-purple-400" />
      <span>PHYSICAL ESTIMATE</span>
    </span>
  );
};
