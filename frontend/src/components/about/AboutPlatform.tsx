import React from 'react';
import {
  Shield,
  Award,
  Database,
  Cpu,
  BookOpen,
  CheckCircle2,
  ExternalLink,
  Lock,
  Compass,
  FileText,
  AlertTriangle,
  Github,
  Heart,
} from 'lucide-react';

export const AboutPlatform: React.FC = () => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Hero Header */}
      <div className="text-center space-y-4 pt-4 pb-2">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full liquid-glass-control text-emerald-400 text-xs font-semibold tracking-wider shadow-glass-sm">
          <Award className="w-3.5 h-3.5 text-emerald-400" />
          <span>Hack2Skill PromptWars — Challenge 6: Urban Air Quality Assistant</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
          About <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">AirGuard AI</span>
        </h1>
        <p className="text-slate-300 text-sm sm:text-base max-w-3xl mx-auto leading-relaxed">
          A high-precision environmental intelligence platform engineered to protect families and urban
          communities from severe smog episodes, navigate daily atmospheric exposure, estimate indoor air
          quality with physical box modeling, and promote sustainable urban mobility.
        </p>
      </div>

      {/* Core Architectural Tenets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-6 space-y-3 shadow-glass-sm transition-all duration-300">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/25 flex items-center justify-center text-cyan-400 shadow-glass-sm">
            <Shield className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Zero-Fabrication Policy</h3>
          <p className="text-xs text-slate-300/80 leading-relaxed">
            Every reading, forecast curve, and pollutant value originates strictly from verified atmospheric
            models or live public telemetry. AirGuard never generates synthetic AQI or hallucinates safe windows.
          </p>
        </div>

        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-6 space-y-3 shadow-glass-sm transition-all duration-300">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/25 flex items-center justify-center text-emerald-400 shadow-glass-sm">
            <Compass className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Scientific Physical Modeling</h3>
          <p className="text-xs text-slate-300/80 leading-relaxed">
            Indoor predictions utilize an engineering single-zone mass-balance box model factoring envelope
            infiltration rates, natural deposition, and Clean Air Delivery Rate (CADR) equivalent air changes.
          </p>
        </div>

        <div className="liquid-glass-card liquid-glass-hover rounded-2xl p-6 space-y-3 shadow-glass-sm transition-all duration-300">
          <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/25 flex items-center justify-center text-amber-400 shadow-glass-sm">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Health-First Privacy</h3>
          <p className="text-xs text-slate-300/80 leading-relaxed">
            Personal health vulnerability profiles (Asthmatic, Elderly, Cardiovascular) are processed locally
            with strict sanitization and privacy-filtered logging to guarantee personal confidentiality.
          </p>
        </div>
      </div>

      {/* Verified Scientific Data Sources & Provenance */}
      <div className="liquid-glass-card rounded-2xl p-6 sm:p-8 space-y-6 shadow-glass-md">
        <div className="flex items-center gap-3 border-b border-white/10 pb-4">
          <div className="p-2 rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/25 shadow-glass-sm">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Atmospheric Data Provenance & Methodology</h3>
            <p className="text-xs text-slate-400">
              Clear accountability of external data feeds, calculation breakpoints, and limitations
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-300">
          <div className="space-y-4">
            <div className="p-4.5 rounded-xl liquid-glass-control border border-white/10 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between text-cyan-300 font-semibold mb-1.5">
                <span className="text-sm">ECMWF CAMS Global Atmospheric Model</span>
                <span className="text-[10px] text-cyan-400/80 font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20">0.4° Grid Resolution</span>
              </div>
              <p className="text-slate-300/80 leading-relaxed">
                Primary atmospheric provider via Open-Meteo Air Quality API. Uses European Centre for Medium-Range
                Weather Forecasts (ECMWF) Integrated Forecasting System (IFS-AER) global atmospheric composition model.
              </p>
            </div>

            <div className="p-4.5 rounded-xl liquid-glass-control border border-white/10 hover:border-emerald-500/30 transition-all">
              <div className="flex items-center justify-between text-emerald-300 font-semibold mb-1.5">
                <span className="text-sm">CPCB India NAQI Sub-Index Calculator</span>
                <span className="text-[10px] text-emerald-400/80 font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">CPCB Guidelines 2014</span>
              </div>
              <p className="text-slate-300/80 leading-relaxed">
                Implements official Central Pollution Control Board piece-wise linear breakpoint interpolation for PM2.5,
                PM10, NO2, O3, SO2, and CO. Requires at least 3 pollutants with PM2.5 or PM10 as dominant determinant.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4.5 rounded-xl liquid-glass-control border border-white/10 hover:border-amber-500/30 transition-all">
              <div className="flex items-center justify-between text-amber-300 font-semibold mb-1.5">
                <span className="text-sm">US EPA Clean Air Act Breakpoints</span>
                <span className="text-[10px] text-amber-400/80 font-mono px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20">EPA-454/B-18-007</span>
              </div>
              <p className="text-slate-300/80 leading-relaxed">
                Standard US EPA Air Quality Index calculation framework enabling global comparisons and sensitivity
                guidance according to revised 2024 PM2.5 annual and daily standards.
              </p>
            </div>

            <div className="p-4.5 rounded-xl liquid-glass-control border border-white/10 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between text-cyan-300 font-semibold mb-1.5">
                <span className="text-sm">WHO 2021 Global Air Quality Guidelines</span>
                <span className="text-[10px] text-cyan-400/80 font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20">WHO Benchmark</span>
              </div>
              <p className="text-slate-300/80 leading-relaxed">
                Direct benchmark comparison against WHO health guidelines (e.g., 24-hour PM2.5 benchmark level of 15 µg/m³),
                contextualizing model concentrations against clinical public health standards.
              </p>
            </div>
          </div>
        </div>

        {/* Regulatory Disclaimer Notice */}
        <div className="p-4.5 rounded-xl bg-amber-500/10 border border-amber-500/25 flex items-start gap-3.5 shadow-glass-sm backdrop-blur-md">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-200/90 leading-relaxed">
            <strong className="text-amber-300 font-semibold">Regulatory Notice:</strong> AirGuard AI computes a
            model proxy index derived from ECMWF CAMS grid projections and does not substitute for certified statutory
            Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by governmental regulatory bodies.
          </div>
        </div>
      </div>

      {/* Engineering & Technology Stack */}
      <div className="liquid-glass-card rounded-2xl p-6 sm:p-8 space-y-6 shadow-glass-md">
        <div className="flex items-center gap-3 border-b border-white/10 pb-4">
          <div className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 shadow-glass-sm">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Full-Stack Technology Architecture</h3>
            <p className="text-xs text-slate-400">Engineered for production resilience, low latency, and testability</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 border border-white/10 transition-all">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Backend Core</span>
            <h4 className="text-sm font-bold text-white mt-1">FastAPI & Python</h4>
            <p className="text-xs text-slate-300/80 mt-2 leading-relaxed">
              Asynchronous ASGI framework, Pydantic v2 data validation, and sliding-window rate limiting.
            </p>
          </div>

          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 border border-white/10 transition-all">
            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Spatial Data</span>
            <h4 className="text-sm font-bold text-white mt-1">PostGIS & PostgreSQL</h4>
            <p className="text-xs text-slate-300/80 mt-2 leading-relaxed">
              Geodesic spatial indexing with GiST, ST_DWithin radius filtering, and Alembic migrations.
            </p>
          </div>

          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 border border-white/10 transition-all">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Frontend Engine</span>
            <h4 className="text-sm font-bold text-white mt-1">React 18 & Vite</h4>
            <p className="text-xs text-slate-300/80 mt-2 leading-relaxed">
              TypeScript strict typing, Apple Liquid Glass design system, and responsive layout.
            </p>
          </div>

          <div className="liquid-glass-control liquid-glass-hover rounded-xl p-4.5 border border-white/10 transition-all">
            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Visualizations</span>
            <h4 className="text-sm font-bold text-white mt-1">Leaflet & Recharts</h4>
            <p className="text-xs text-slate-300/80 mt-2 leading-relaxed">
              Interactive GIS hazard mapping with custom tile layers, diurnal trend curves, and carbon bar charts.
            </p>
          </div>
        </div>
      </div>

      {/* Developer & Challenge Credits */}
      <div className="border-t border-white/10 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
        <div className="flex items-center gap-2">
          <span>Developed with</span>
          <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
          <span>for Hack2Skill PromptWars Challenge 6</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-200 font-mono font-medium">AirGuard AI v1.0.0 Production</span>
          <span className="text-slate-600">•</span>
          <span className="text-emerald-400 font-medium">Open Architecture</span>
        </div>
      </div>
    </div>
  );
};
