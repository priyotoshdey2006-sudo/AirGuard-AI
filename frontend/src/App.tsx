import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Navbar, CITIES } from './components/layout/Navbar';
import { AQIDashboard } from './components/aqi/AQIDashboard';
import { ForecastView } from './components/forecast/ForecastView';
import { DailyRoutinePlanner } from './components/recommendations/DailyRoutinePlanner';
import { IndoorAdvisor } from './components/indoor/IndoorAdvisor';
import { EcoCommutePlanner } from './components/transport/EcoCommutePlanner';
import { CommunityHazardMap } from './components/community/CommunityHazardMap';
import { EnvironmentalImpactTracker } from './components/impact/EnvironmentalImpactTracker';
import { AboutPlatform } from './components/about/AboutPlatform';
import { AICopilotDrawer } from './components/assistant/AICopilotDrawer';
import { api } from './services/api';
import {
  ChatMessage,
  CommunityReport,
  CurrentAQI,
  ForecastData,
  IndoorGuidance,
  RouteComparison,
  RoutinePlan,
  SensitivityLevel,
} from './types';
import { Shield, Sparkles } from 'lucide-react';

export function App() {
  const location = useLocation();
  const [selectedCityName, setSelectedCityName] = useState(CITIES[0].name);
  const [sensitivity, setSensitivity] = useState<SensitivityLevel>('ASTHMATIC');

  // Selected City coordinates
  const currentCity = CITIES.find((c) => c.name === selectedCityName) || CITIES[0];

  // Core Data State
  const [currentAQI, setCurrentAQI] = useState<CurrentAQI | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [routine, setRoutine] = useState<RoutinePlan | null>(null);
  const [indoorGuidance, setIndoorGuidance] = useState<IndoorGuidance | null>(null);
  const [routeComparison, setRouteComparison] = useState<RouteComparison | null>(null);
  const [communityReports, setCommunityReports] = useState<CommunityReport[]>([]);

  // Loading flags
  const [loadingAQI, setLoadingAQI] = useState(false);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [loadingRoutine, setLoadingRoutine] = useState(false);
  const [loadingIndoor, setLoadingIndoor] = useState(false);
  const [loadingTransport, setLoadingTransport] = useState(false);
  const [loadingCommunity, setLoadingCommunity] = useState(false);

  // AI Assistant Drawer State
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: 'Hello! I am AirGuard Copilot. I can evaluate your respiratory risk, advise on certified N95 respirators, and schedule safe outdoor activity windows grounded in live atmospheric measurements.',
      timestamp: new Date().toISOString(),
    },
  ]);

  // Initial Data Fetch when City changes
  const loadCityData = async () => {
    setLoadingAQI(true);
    setLoadingForecast(true);
    setLoadingCommunity(true);

    try {
      const [aqiData, forecastData, reportsData] = await Promise.all([
        api.getCurrentAQI(currentCity.lat, currentCity.lon),
        api.getForecast(currentCity.lat, currentCity.lon),
        api.getCommunityReports(currentCity.lat, currentCity.lon),
      ]);
      setCurrentAQI(aqiData);
      setForecast(forecastData);
      setCommunityReports(reportsData.reports);
    } catch (err) {
      console.error('Error fetching live atmospheric data:', err);
    } finally {
      setLoadingAQI(false);
      setLoadingForecast(false);
      setLoadingCommunity(false);
    }
  };

  useEffect(() => {
    loadCityData();
  }, [selectedCityName]);

  // Lazy load Indoor & Transport when routes are visited
  useEffect(() => {
    if (location.pathname === '/indoor' && !indoorGuidance) {
      handleCalculateIndoor(400, true);
    }
    if (location.pathname === '/transport' && !routeComparison) {
      handleCompareRoutes('Central Station', 'Business District');
    }
    if (location.pathname === '/advisor') {
      setIsAssistantOpen(true);
    }
  }, [location.pathname]);

  // Handlers
  const handleGenerateRoutine = async (activities: string[]) => {
    setLoadingRoutine(true);
    try {
      const res = await api.getDailyRoutine(
        currentCity.lat,
        currentCity.lon,
        sensitivity,
        activities
      );
      setRoutine(res);
    } catch (err) {
      console.error('Failed to generate daily routine:', err);
    } finally {
      setLoadingRoutine(false);
    }
  };

  const handleCalculateIndoor = async (roomSqft: number, hasHepa: boolean) => {
    setLoadingIndoor(true);
    try {
      const res = await api.getIndoorGuidance(
        currentCity.lat,
        currentCity.lon,
        roomSqft,
        hasHepa
      );
      setIndoorGuidance(res);
    } catch (err) {
      console.error('Failed to calculate indoor guidance:', err);
    } finally {
      setLoadingIndoor(false);
    }
  };

  const handleCompareRoutes = async (origin: string, destination: string) => {
    setLoadingTransport(true);
    try {
      const res = await api.compareRoutes(
        currentCity.lat,
        currentCity.lon,
        currentCity.lat + 0.05,
        currentCity.lon + 0.08,
        origin,
        destination
      );
      setRouteComparison(res);
    } catch (err) {
      console.error('Failed to compare routes:', err);
    } finally {
      setLoadingTransport(false);
    }
  };

  const handleSubmitReport = async (reportData: {
    title: string;
    description: string;
    category: string;
    severity: number;
    latitude: number;
    longitude: number;
    reporter_name: string;
  }) => {
    try {
      const newReport = await api.submitCommunityReport(reportData);
      setCommunityReports([newReport, ...communityReports]);
    } catch (err) {
      console.error('Failed to submit report:', err);
    }
  };

  const handleUpvoteReport = async (reportId: string) => {
    try {
      const res = await api.upvoteReport(reportId);
      setCommunityReports(
        communityReports.map((r) =>
          r.id === reportId ? { ...r, upvotes_count: res.upvotes_count, status: res.status } : r
        )
      );
    } catch (err) {
      console.error('Failed to upvote report:', err);
    }
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toISOString(),
    };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatLoading(true);

    try {
      const res = await api.sendChatMessage(
        text,
        currentCity.lat,
        currentCity.lon,
        sensitivity
      );
      const botMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'assistant',
        text: res.reply,
        timestamp: new Date().toISOString(),
        model_provider: res.model_provider,
      };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const botErr: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'assistant',
        text: 'I encountered an issue querying the atmospheric copilot. Please verify your connection.',
        timestamp: new Date().toISOString(),
      };
      setChatMessages((prev) => [...prev, botErr]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-midnight-950 text-slate-100 flex flex-col font-sans relative selection:bg-emerald-500/25 selection:text-emerald-200">
      {/* Liquid Glass Ambient Background Layers */}
      <div className="bg-liquid-mesh" aria-hidden="true" />
      <div className="bg-liquid-grid" aria-hidden="true" />

      {/* Primary Floating Navigation */}
      <Navbar
        selectedCity={selectedCityName}
        setSelectedCity={setSelectedCityName}
        sensitivity={sensitivity}
        setSensitivity={setSensitivity}
        onOpenAssistant={() => setIsAssistantOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <Routes>
          {/* Module 1: Air Quality Dashboard */}
          <Route
            path="/"
            element={
              <AQIDashboard
                data={currentAQI}
                loading={loadingAQI}
                onRefresh={loadCityData}
              />
            }
          />

          {/* Module 3: Pollution Forecast */}
          <Route
            path="/forecast"
            element={<ForecastView forecast={forecast} loading={loadingForecast} />}
          />

          {/* Module 5: Personalized Daily Routine Planner */}
          <Route
            path="/planner"
            element={
              <DailyRoutinePlanner
                routine={routine}
                loading={loadingRoutine}
                sensitivity={sensitivity}
                onGenerate={handleGenerateRoutine}
              />
            }
          />

          {/* Module 6: Indoor Air Quality Guide */}
          <Route
            path="/indoor"
            element={
              <IndoorAdvisor
                guidance={indoorGuidance}
                loading={loadingIndoor}
                onCalculate={handleCalculateIndoor}
              />
            }
          />

          {/* Module 7: Sustainable Alternatives / Eco-Commute */}
          <Route
            path="/transport"
            element={
              <EcoCommutePlanner
                comparison={routeComparison}
                loading={loadingTransport}
                onCompare={handleCompareRoutes}
              />
            }
          />

          {/* Module 2: Location Search and Pollution Hazard Map */}
          <Route
            path="/map"
            element={
              <CommunityHazardMap
                reports={communityReports}
                loading={loadingCommunity}
                userLat={currentCity.lat}
                userLon={currentCity.lon}
                onSubmitReport={handleSubmitReport}
                onUpvote={handleUpvoteReport}
              />
            }
          />

          {/* Module 8: Environmental Impact Tracker */}
          <Route path="/impact" element={<EnvironmentalImpactTracker />} />

          {/* Module 9: About and Developer Information */}
          <Route path="/about" element={<AboutPlatform />} />

          {/* Fallback to Dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {/* Module 4: Floating AI Environmental Advisor Copilot */}
      <AICopilotDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        messages={chatMessages}
        loading={chatLoading}
        onSendMessage={handleSendMessage}
        currentAQI={currentAQI?.aqi_us || 50}
        sensitivity={sensitivity}
      />

      {/* Liquid Glass Footer */}
      <footer className="relative z-10 border-t border-white/[0.06] bg-midnight-950/60 backdrop-blur-xl py-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-5 h-5 rounded-md bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Shield className="w-3 h-3" />
            </div>
            <p className="text-slate-300 font-medium">
              AirGuard AI — Urban Environmental Intelligence Platform
            </p>
          </div>
          <div className="flex items-center gap-4 text-slate-400 text-[11px]">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live CAMS & Open-Meteo Telemetry
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-emerald-400 font-medium">Zero-Fabrication Guarantee</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
