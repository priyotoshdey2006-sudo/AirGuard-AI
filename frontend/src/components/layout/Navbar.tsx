import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Shield,
  MapPin,
  Activity,
  Wind,
  Home,
  Navigation,
  Users,
  MessageSquare,
  Leaf,
  Info,
  ChevronDown,
  Sparkles,
  Menu,
  X,
} from 'lucide-react';
import { SensitivityLevel } from '../../types';

interface Props {
  selectedCity: string;
  setSelectedCity: (city: string) => void;
  sensitivity: SensitivityLevel;
  setSensitivity: (sens: SensitivityLevel) => void;
  onOpenAssistant: () => void;
}

export const CITIES = [
  { name: 'New Delhi, India', lat: 28.6139, lon: 77.2090 },
  { name: 'Mumbai, India', lat: 19.0760, lon: 72.8777 },
  { name: 'London, UK', lat: 51.5074, lon: -0.1278 },
  { name: 'New York, USA', lat: 40.7128, lon: -74.0060 },
  { name: 'Beijing, China', lat: 39.9042, lon: 116.4074 },
  { name: 'Tokyo, Japan', lat: 35.6762, lon: 139.6503 },
];

export const Navbar: React.FC<Props> = ({
  selectedCity,
  setSelectedCity,
  sensitivity,
  setSensitivity,
  onOpenAssistant,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs = [
    { path: '/', label: 'AQI Dashboard', icon: Activity },
    { path: '/forecast', label: '24h Forecast', icon: Wind },
    { path: '/planner', label: 'Daily Planner', icon: Shield },
    { path: '/indoor', label: 'Indoor Guidance', icon: Home },
    { path: '/transport', label: 'Eco-Commute', icon: Navigation },
    { path: '/map', label: 'Pollution Map', icon: Users },
    { path: '/impact', label: 'Impact Tracker', icon: Leaf },
    { path: '/about', label: 'About & Data', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-40 w-full px-3 sm:px-6 pt-3 sm:pt-4 transition-all">
      <div className="max-w-7xl mx-auto liquid-glass-nav rounded-2xl sm:rounded-3xl px-4 sm:px-6 py-2.5 sm:py-3 transition-all">
        {/* Top Floating Control Row */}
        <div className="flex items-center justify-between gap-3">
          {/* Logo & Brand Identity */}
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-3 cursor-pointer group select-none shrink-0"
          >
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-[1px] shadow-[0_0_20px_rgba(16,185,129,0.3)] group-hover:scale-105 transition-transform duration-300">
              <div className="w-full h-full bg-midnight-900/90 rounded-[11px] flex items-center justify-center backdrop-blur-md">
                <Shield className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base sm:text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-emerald-200 bg-clip-text text-transparent">
                  AirGuard
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.2)]">
                  AI
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="hidden sm:inline">Urban Environmental Intelligence</span>
                <span className="sm:hidden">Live CAMS</span>
              </div>
            </div>
          </div>

          {/* Quick Context Selectors (Desktop & Tablet) */}
          <div className="hidden lg:flex items-center gap-2.5">
            {/* City Selector Pill */}
            <div className="relative flex items-center gap-2 liquid-glass-control rounded-full px-3 py-1.5 text-xs text-slate-300">
              <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <select
                aria-label="Select Target City"
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="bg-transparent border-none text-slate-200 text-xs font-medium focus:outline-none cursor-pointer pr-4 appearance-none"
              >
                {CITIES.map((c) => (
                  <option key={c.name} value={c.name} className="bg-midnight-900 text-slate-100">
                    {c.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 pointer-events-none absolute right-3" />
            </div>

            {/* Health Vulnerability Selector Pill */}
            <div className="relative flex items-center gap-2 liquid-glass-control rounded-full px-3 py-1.5 text-xs text-slate-300">
              <span className="text-slate-400 text-[11px] font-medium">Profile:</span>
              <select
                aria-label="Select Health Sensitivity Profile"
                value={sensitivity}
                onChange={(e) => setSensitivity(e.target.value as SensitivityLevel)}
                className="bg-transparent border-none text-emerald-300 text-xs font-semibold focus:outline-none cursor-pointer pr-4 appearance-none"
              >
                <option value="NORMAL" className="bg-midnight-900 text-slate-200">General Public</option>
                <option value="ASTHMATIC" className="bg-midnight-900 text-slate-200">Asthmatic</option>
                <option value="CARDIOVASCULAR" className="bg-midnight-900 text-slate-200">Cardiovascular</option>
                <option value="ELDERLY" className="bg-midnight-900 text-slate-200">Elderly</option>
                <option value="CHILD" className="bg-midnight-900 text-slate-200">Child</option>
                <option value="ATHLETE" className="bg-midnight-900 text-slate-200">Outdoor Athlete</option>
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 pointer-events-none absolute right-3" />
            </div>
          </div>

          {/* Action Area: AI Copilot & Mobile Toggle */}
          <div className="flex items-center gap-2">
            {/* Liquid Glass Copilot Button */}
            <button
              onClick={onOpenAssistant}
              className="relative group overflow-hidden flex items-center gap-2 px-3.5 py-1.5 sm:py-2 rounded-full text-xs font-semibold text-midnight-950 bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-300 shadow-[0_4px_20px_rgba(16,185,129,0.35)] hover:shadow-[0_6px_25px_rgba(16,185,129,0.5)] active:scale-95 transition-all duration-300"
            >
              <Sparkles className="w-3.5 h-3.5 text-midnight-950" />
              <span className="font-bold tracking-tight">AI Copilot</span>
              <span className="hidden sm:inline-block px-1.5 py-0.2 text-[9px] font-mono bg-midnight-950/20 text-midnight-950 rounded-md">
                ⌘K
              </span>
              {/* Specular sheen swipe on hover */}
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/30 to-transparent pointer-events-none" />
            </button>

            {/* Mobile Menu Toggle Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden liquid-glass-control p-2 rounded-xl text-slate-300 hover:text-white"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Mobile Expanded Selectors (Shown only when menu open or small screen) */}
        {mobileMenuOpen && (
          <div className="lg:hidden mt-3 pt-3 border-t border-white/[0.08] grid grid-cols-1 sm:grid-cols-2 gap-2 animate-fadeIn">
            <div className="relative flex items-center gap-2 liquid-glass-control rounded-xl px-3 py-2 text-xs text-slate-300">
              <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <select
                aria-label="Select Target City"
                value={selectedCity}
                onChange={(e) => {
                  setSelectedCity(e.target.value);
                  setMobileMenuOpen(false);
                }}
                className="w-full bg-transparent border-none text-slate-200 text-xs font-medium focus:outline-none cursor-pointer pr-4 appearance-none"
              >
                {CITIES.map((c) => (
                  <option key={c.name} value={c.name} className="bg-midnight-900 text-slate-100">
                    {c.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 pointer-events-none absolute right-3" />
            </div>

            <div className="relative flex items-center gap-2 liquid-glass-control rounded-xl px-3 py-2 text-xs text-slate-300">
              <span className="text-slate-400 text-xs">Profile:</span>
              <select
                aria-label="Select Health Sensitivity Profile"
                value={sensitivity}
                onChange={(e) => {
                  setSensitivity(e.target.value as SensitivityLevel);
                  setMobileMenuOpen(false);
                }}
                className="w-full bg-transparent border-none text-emerald-300 text-xs font-semibold focus:outline-none cursor-pointer pr-4 appearance-none"
              >
                <option value="NORMAL" className="bg-midnight-900 text-slate-200">General Public</option>
                <option value="ASTHMATIC" className="bg-midnight-900 text-slate-200">Asthmatic</option>
                <option value="CARDIOVASCULAR" className="bg-midnight-900 text-slate-200">Cardiovascular</option>
                <option value="ELDERLY" className="bg-midnight-900 text-slate-200">Elderly</option>
                <option value="CHILD" className="bg-midnight-900 text-slate-200">Child</option>
                <option value="ATHLETE" className="bg-midnight-900 text-slate-200">Outdoor Athlete</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 pointer-events-none absolute right-3" />
            </div>
          </div>
        )}

        {/* Apple Segmented Floating Navigation Bar */}
        <nav
          aria-label="Main Navigation"
          className="mt-2.5 pt-2 border-t border-white/[0.06] flex items-center gap-1 overflow-x-auto pb-1 scrollbar-none"
        >
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = location.pathname === tab.path;
            return (
              <button
                key={tab.path}
                onClick={() => {
                  navigate(tab.path);
                  setMobileMenuOpen(false);
                }}
                className={`relative group flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all duration-300 ${
                  isActive
                    ? 'text-white font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                {/* Active Segment Liquid Pill with Specular Bevel */}
                {isActive && (
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-cyan-500/15 border border-emerald-400/35 shadow-[0_0_16px_rgba(16,185,129,0.2),inset_0_1px_0_rgba(255,255,255,0.25)] pointer-events-none" />
                )}
                <Icon
                  className={`w-3.5 h-3.5 relative z-10 transition-colors ${
                    isActive ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                <span className="relative z-10">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
