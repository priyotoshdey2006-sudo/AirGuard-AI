import React from 'react';
import { Shield, MapPin, Activity, Wind, Home, Navigation, Users, MessageSquare } from 'lucide-react';
import { SensitivityLevel } from '../../types';

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
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
  activeTab,
  setActiveTab,
  selectedCity,
  setSelectedCity,
  sensitivity,
  setSensitivity,
  onOpenAssistant,
}) => {
  const tabs = [
    { id: 'dashboard', label: 'AQI Intelligence', icon: Activity },
    { id: 'forecast', label: '24h Forecast', icon: Wind },
    { id: 'routine', label: 'AI Routine', icon: Shield },
    { id: 'indoor', label: 'Indoor Guidance', icon: Home },
    { id: 'transport', label: 'Eco-Commute', icon: Navigation },
    { id: 'community', label: 'Community Map', icon: Users },
  ];

  return (
    <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Shield className="w-5 h-5 text-slate-950 font-black" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-teal-300 via-emerald-300 to-teal-400 bg-clip-text text-transparent">
                  AirGuard AI
                </span>
                <span className="px-1.5 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Urban Environmental Intelligence</p>
            </div>
          </div>

          {/* Location & Health Sensitivity Selectors */}
          <div className="flex items-center gap-3">
            {/* City selector */}
            <div className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
              <MapPin className="w-3.5 h-3.5 text-teal-400" />
              <select
                aria-label="Select Target City"
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="bg-transparent border-none text-slate-200 text-xs focus:outline-none cursor-pointer pr-1"
              >
                {CITIES.map((c) => (
                  <option key={c.name} value={c.name} className="bg-slate-900 text-slate-100">
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Health Profile selector */}
            <div className="hidden md:flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
              <span className="text-slate-400">Profile:</span>
              <select
                aria-label="Select Health Sensitivity Profile"
                value={sensitivity}
                onChange={(e) => setSensitivity(e.target.value as SensitivityLevel)}
                className="bg-transparent border-none text-teal-300 font-semibold text-xs focus:outline-none cursor-pointer"
              >
                <option value="NORMAL" className="bg-slate-900">General Public</option>
                <option value="ASTHMATIC" className="bg-slate-900">Asthmatic</option>
                <option value="CARDIOVASCULAR" className="bg-slate-900">Cardiovascular</option>
                <option value="ELDERLY" className="bg-slate-900">Elderly</option>
                <option value="CHILD" className="bg-slate-900">Child</option>
                <option value="ATHLETE" className="bg-slate-900">Outdoor Athlete</option>
              </select>
            </div>

            {/* AI Assistant Quick Pill Button */}
            <button
              onClick={onOpenAssistant}
              className="flex items-center gap-1.5 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-semibold text-xs px-3 py-1.5 rounded-lg shadow-md transition-all active:scale-95"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ask AI Copilot</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 border-t border-slate-800/60 overflow-x-auto py-2 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
