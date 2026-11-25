import React, { useState, useMemo } from 'react';
import {
  Leaf,
  ShieldCheck,
  TrendingDown,
  Wind,
  Trees,
  Award,
  Info,
  Car,
  Train,
  Bike,
  Activity,
  Calendar,
  Sparkles,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area,
  Legend,
} from 'recharts';

export const EnvironmentalImpactTracker: React.FC = () => {
  // Interactive Simulation Inputs
  const [commuteDistanceKm, setCommuteDistanceKm] = useState<number>(22);
  const [cleanTransitDays, setCleanTransitDays] = useState<number>(5);
  const [maskCompliancePercent, setMaskCompliancePercent] = useState<number>(85);
  const [hepaUsageHours, setHepaUsageHours] = useState<number>(8);
  const [ambientAQI, setAmbientAQI] = useState<number>(185);

  // Scientific Constants (IPCC & Berkeley Earth metrics)
  // ICE Car: ~0.192 kg CO2 / km
  // Metro: ~0.028 kg CO2 / passenger-km
  // Electric Bus: ~0.045 kg CO2 / passenger-km
  // Bicycle / Walk: 0.000 kg CO2 / km
  // 1 tree absorbs ~21.77 kg CO2 per year (~0.418 kg per week)
  // 1 cigarette equivalent ≈ 22 ug/m3 PM2.5 inhaled continuously over 24h
  // Minute ventilation: ~12 L/min during commute = 0.72 m3/hour

  const calculations = useMemo(() => {
    const weeklyKm = commuteDistanceKm * cleanTransitDays * 2; // round trip
    const iceCarCo2 = weeklyKm * 0.192;
    const metroCo2 = weeklyKm * 0.028;
    const weeklyCo2SavedKg = Math.max(0, iceCarCo2 - metroCo2);
    const annualCo2SavedKg = weeklyCo2SavedKg * 52;
    const treesEquivalent = weeklyCo2SavedKg / 0.418;

    // Inhaled PM2.5 avoidance:
    // Outdoor PM2.5 estimate based on AQI (approximate linear mapping for screening)
    const outdoorPm25 = Math.max(10, (ambientAQI * 0.65));
    const hoursOutdoorsPerWeek = (cleanTransitDays * 1.5);
    const airVolumeInhaledM3 = hoursOutdoorsPerWeek * 0.72; // m3
    const totalPotentialPm25Ug = outdoorPm25 * airVolumeInhaledM3;
    const avoidedMaskPm25Ug = totalPotentialPm25Ug * (maskCompliancePercent / 100) * 0.95; // 95% N95 efficiency

    // Indoor avoided PM2.5 from HEPA (assumes indoor reduces from outdoor by 75% with HEPA):
    const indoorRestingVentilationM3 = hepaUsageHours * 7 * 0.45; // m3 resting air
    const avoidedHepaPm25Ug = indoorRestingVentilationM3 * (outdoorPm25 * 0.75);
    const totalAvoidedPm25Ug = avoidedMaskPm25Ug + avoidedHepaPm25Ug;

    // Cigarettes avoided per week:
    const dailyEquivalentCigarettes = (totalAvoidedPm25Ug / (22 * 0.72 * 24)) / 7;

    return {
      weeklyKm,
      weeklyCo2SavedKg: Number(weeklyCo2SavedKg.toFixed(1)),
      annualCo2SavedKg: Number(annualCo2SavedKg.toFixed(0)),
      treesEquivalent: Number(treesEquivalent.toFixed(1)),
      totalAvoidedPm25Ug: Number((totalAvoidedPm25Ug / 1000).toFixed(2)), // in mg
      dailyEquivalentCigarettes: Number(dailyEquivalentCigarettes.toFixed(1)),
    };
  }, [commuteDistanceKm, cleanTransitDays, maskCompliancePercent, hepaUsageHours, ambientAQI]);

  // Chart data: Commute mode CO2 comparison for current distance
  const modalComparisonData = [
    { mode: 'Petrol Car', co2: Number((commuteDistanceKm * 2 * 0.192).toFixed(2)), fill: '#ef4444' },
    { mode: 'Cab / Ride', co2: Number((commuteDistanceKm * 2 * 0.165).toFixed(2)), fill: '#f97316' },
    { mode: 'Hybrid Car', co2: Number((commuteDistanceKm * 2 * 0.110).toFixed(2)), fill: '#eab308' },
    { mode: 'Electric Bus', co2: Number((commuteDistanceKm * 2 * 0.045).toFixed(2)), fill: '#3b82f6' },
    { mode: 'Metro Rail', co2: Number((commuteDistanceKm * 2 * 0.028).toFixed(2)), fill: '#10b981' },
    { mode: 'Cycle / Walk', co2: 0, fill: '#14b8a6' },
  ];

  // 4-Week Cumulative Projection Data
  const weeklyProjectionData = [
    { week: 'Week 1', co2Saved: calculations.weeklyCo2SavedKg, pmAvoidedMg: calculations.totalAvoidedPm25Ug },
    { week: 'Week 2', co2Saved: Number((calculations.weeklyCo2SavedKg * 2).toFixed(1)), pmAvoidedMg: Number((calculations.totalAvoidedPm25Ug * 2).toFixed(1)) },
    { week: 'Week 3', co2Saved: Number((calculations.weeklyCo2SavedKg * 3).toFixed(1)), pmAvoidedMg: Number((calculations.totalAvoidedPm25Ug * 3).toFixed(1)) },
    { week: 'Week 4', co2Saved: Number((calculations.weeklyCo2SavedKg * 4).toFixed(1)), pmAvoidedMg: Number((calculations.totalAvoidedPm25Ug * 4).toFixed(1)) },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner */}
      <div className="liquid-glass-card rounded-2xl p-6 sm:p-7 shadow-glass-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-glass-sm">
                <Leaf className="w-5 h-5" />
              </span>
              <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
                Personal Environmental Impact Tracker
              </h2>
            </div>
            <p className="text-sm text-slate-300/90 mt-2 max-w-2xl leading-relaxed">
              Quantify your tangible contributions to urban clean air. Calculate cumulative avoided
              respiratory particulate doses, carbon emissions offset via public transit, and equivalent
              tree-absorption metrics.
            </p>
          </div>

          <div className="flex items-center gap-2 liquid-glass-control rounded-xl px-4 py-2.5 text-xs text-slate-200 shadow-glass-sm shrink-0">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="font-medium">Scientific Basis: IPCC & Berkeley Earth Models</span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Weekly CO2 Saved */}
        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-5 shadow-glass-sm transition-all duration-300">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold tracking-wider uppercase text-slate-300">Weekly CO₂ Offset</span>
            <TrendingDown className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {calculations.weeklyCo2SavedKg}{' '}
            <span className="text-sm font-medium text-emerald-400">kg CO₂</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Projected: <span className="text-emerald-300 font-semibold">{calculations.annualCo2SavedKg} kg/year</span>
          </p>
        </div>

        {/* Metric 2: Particulate Avoidance */}
        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-5 shadow-glass-sm transition-all duration-300">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold tracking-wider uppercase text-slate-300">PM2.5 Dose Avoided</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {calculations.totalAvoidedPm25Ug}{' '}
            <span className="text-sm font-medium text-cyan-400">mg</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Filtered from lungs via N95 + Indoor HEPA
          </p>
        </div>

        {/* Metric 3: Tree Equivalent */}
        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-5 shadow-glass-sm transition-all duration-300">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold tracking-wider uppercase text-slate-300">Tree-Absorption Eq.</span>
            <Trees className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {calculations.treesEquivalent}{' '}
            <span className="text-sm font-medium text-emerald-400">trees/wk</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Equivalent carbon absorption by mature trees
          </p>
        </div>

        {/* Metric 4: Health Protection Factor */}
        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-5 shadow-glass-sm transition-all duration-300">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold tracking-wider uppercase text-slate-300">Cigarette Eq. Prevented</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {calculations.dailyEquivalentCigarettes}{' '}
            <span className="text-sm font-medium text-amber-400">cigs/day</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Equivalent particulate toxicity avoided
          </p>
        </div>
      </div>

      {/* Interactive Controls & Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Controls Column */}
        <div className="lg:col-span-5 liquid-glass-card rounded-2xl p-6 space-y-6 shadow-glass-md">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="font-semibold text-white text-base flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              <span>Simulate Your Lifestyle Impact</span>
            </h3>
            <span className="text-[11px] text-cyan-400 font-mono font-medium px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20">
              Live Recalculation
            </span>
          </div>

          {/* Slider 1: Commute Distance */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">One-Way Commute Distance:</span>
              <span className="text-emerald-400 font-semibold">{commuteDistanceKm} km</span>
            </div>
            <input
              type="range"
              min="2"
              max="60"
              step="1"
              value={commuteDistanceKm}
              onChange={(e) => setCommuteDistanceKm(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-emerald-400 focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>2 km (Local)</span>
              <span>30 km (Suburban)</span>
              <span>60 km (Regional)</span>
            </div>
          </div>

          {/* Slider 2: Clean Transit Days */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Metro/Clean Transit Days:</span>
              <span className="text-emerald-400 font-semibold">{cleanTransitDays} days/week</span>
            </div>
            <input
              type="range"
              min="0"
              max="7"
              step="1"
              value={cleanTransitDays}
              onChange={(e) => setCleanTransitDays(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-emerald-400 focus:outline-none focus:ring-1 focus:ring-emerald-400/50"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0 (None)</span>
              <span>3 (Hybrid)</span>
              <span>7 (Every day)</span>
            </div>
          </div>

          {/* Slider 3: Mask Compliance */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Certified N95 Outdoor Compliance:</span>
              <span className="text-cyan-400 font-semibold">{maskCompliancePercent}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={maskCompliancePercent}
              onChange={(e) => setMaskCompliancePercent(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400/50"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0% (No mask)</span>
              <span>50% (Commute only)</span>
              <span>100% (Strict)</span>
            </div>
          </div>

          {/* Slider 4: Indoor HEPA Runtime */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Indoor HEPA Purifier Runtime:</span>
              <span className="text-cyan-400 font-semibold">{hepaUsageHours} hrs/day</span>
            </div>
            <input
              type="range"
              min="0"
              max="24"
              step="1"
              value={hepaUsageHours}
              onChange={(e) => setHepaUsageHours(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400/50"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0 hrs</span>
              <span>8 hrs (Sleep only)</span>
              <span>24 hrs (Full cycle)</span>
            </div>
          </div>

          {/* Slider 5: Current Ambient AQI */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Urban Ambient AQI Baseline:</span>
              <span className="text-amber-400 font-semibold">{ambientAQI} AQI</span>
            </div>
            <input
              type="range"
              min="50"
              max="500"
              step="10"
              value={ambientAQI}
              onChange={(e) => setAmbientAQI(Number(e.target.value))}
              className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400/50"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>50 (Moderate)</span>
              <span>250 (Severe)</span>
              <span>500 (Hazardous)</span>
            </div>
          </div>
        </div>

        {/* Visual Charts Column */}
        <div className="lg:col-span-7 space-y-6">
          {/* Chart 1: Per-Trip Emissions Across Modes */}
          <div className="liquid-glass-card rounded-2xl p-6 shadow-glass-md">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="font-semibold text-white text-sm">
                  Round-Trip Carbon Footprint by Mode ({commuteDistanceKm * 2} km)
                </h4>
                <p className="text-xs text-slate-400">Emissions generated per round-trip commute (kg CO₂)</p>
              </div>
              <Train className="w-4 h-4 text-emerald-400" />
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={modalComparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.07)" vertical={false} />
                  <XAxis dataKey="mode" stroke="#94a3b8" fontSize={11} interval={0} angle={-15} textAnchor="end" />
                  <YAxis stroke="#94a3b8" fontSize={11} unit=" kg" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(9, 16, 33, 0.94)',
                      borderColor: 'rgba(255, 255, 255, 0.12)',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                      boxShadow: '0 12px 32px rgba(0, 0, 0, 0.5)',
                      backdropFilter: 'blur(16px)',
                    }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Bar dataKey="co2" name="kg CO₂" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: 4-Week Cumulative Avoidance Projection */}
          <div className="liquid-glass-card rounded-2xl p-6 shadow-glass-md">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="font-semibold text-white text-sm">
                  4-Week Cumulative Savings Projection
                </h4>
                <p className="text-xs text-slate-400">Cumulative CO₂ avoided (kg) and PM2.5 prevented from inhalation (mg)</p>
              </div>
              <Activity className="w-4 h-4 text-cyan-400" />
            </div>

            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={weeklyProjectionData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                  <defs>
                    <linearGradient id="co2Grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="pmGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.07)" vertical={false} />
                  <XAxis dataKey="week" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(9, 16, 33, 0.94)',
                      borderColor: 'rgba(255, 255, 255, 0.12)',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                      boxShadow: '0 12px 32px rgba(0, 0, 0, 0.5)',
                      backdropFilter: 'blur(16px)',
                    }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Area type="monotone" dataKey="co2Saved" name="Cumulative CO₂ Offset (kg)" stroke="#10b981" fillOpacity={1} fill="url(#co2Grad)" strokeWidth={2.5} />
                  <Area type="monotone" dataKey="pmAvoidedMg" name="Avoided Inhaled PM2.5 (mg)" stroke="#06b6d4" fillOpacity={1} fill="url(#pmGrad)" strokeWidth={2.5} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Citizen Action & Community Milestones */}
      <div className="liquid-glass-card rounded-2xl p-6 shadow-glass-md">
        <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-400" />
          <span>Earned Citizen Stewardship Milestones</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 flex items-start gap-3.5 border border-white/10">
            <div className="p-2.5 rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/25 shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h5 className="font-semibold text-sm text-cyan-300">Clean Air Guardian</h5>
              <p className="text-xs text-slate-300/80 mt-1 leading-relaxed">
                Maintained &gt;80% N95 compliance and indoor HEPA filtration during severe winter smog episodes.
              </p>
            </div>
          </div>

          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 flex items-start gap-3.5 border border-white/10">
            <div className="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 shrink-0">
              <Train className="w-5 h-5" />
            </div>
            <div>
              <h5 className="font-semibold text-sm text-emerald-300">Eco-Commute Champion</h5>
              <p className="text-xs text-slate-300/80 mt-1 leading-relaxed">
                Reduced urban vehicular emissions by choosing electrified metro transit over single-occupancy ICE cars.
              </p>
            </div>
          </div>

          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 flex items-start gap-3.5 border border-white/10">
            <div className="p-2.5 rounded-xl bg-amber-500/15 text-amber-400 border border-amber-500/25 shrink-0">
              <Trees className="w-5 h-5" />
            </div>
            <div>
              <h5 className="font-semibold text-sm text-amber-300">Forest Shield Tier 1</h5>
              <p className="text-xs text-slate-300/80 mt-1 leading-relaxed">
                Offset equivalent carbon sequestration of over 10 mature urban trees this calendar quarter.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
