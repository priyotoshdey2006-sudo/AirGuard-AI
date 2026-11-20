import React, { useState, useEffect } from 'react';
import { Navbar, CITIES } from './components/layout/Navbar';
import { AQIDashboard } from './components/aqi/AQIDashboard';
import { ForecastView } from './components/forecast/ForecastView';
import { DailyRoutinePlanner } from './components/recommendations/DailyRoutinePlanner';
import { IndoorAdvisor } from './components/indoor/IndoorAdvisor';
import { EcoCommutePlanner } from './components/transport/EcoCommutePlanner';
import { CommunityHazardMap } from './components/community/CommunityHazardMap';
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

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
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

  // Lazy load Indoor & Transport if tab opens
  useEffect(() => {
    if (activeTab === 'indoor' && !indoorGuidance) {
      handleCalculateIndoor(400, true);
    }
    if (activeTab === 'transport' && !routeComparison) {
      handleCompareRoutes('Central Station', 'Business District');
    }
  }, [activeTab]);

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
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        selectedCity={selectedCityName}
        setSelectedCity={setSelectedCityName}
        sensitivity={sensitivity}
        setSensitivity={setSensitivity}
        onOpenAssistant={() => setIsAssistantOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <AQIDashboard
            data={currentAQI}
            loading={loadingAQI}
            onRefresh={loadCityData}
          />
        )}

        {activeTab === 'forecast' && (
          <ForecastView forecast={forecast} loading={loadingForecast} />
        )}

        {activeTab === 'routine' && (
          <DailyRoutinePlanner
            routine={routine}
            loading={loadingRoutine}
            sensitivity={sensitivity}
            onGenerate={handleGenerateRoutine}
          />
        )}

        {activeTab === 'indoor' && (
          <IndoorAdvisor
            guidance={indoorGuidance}
            loading={loadingIndoor}
            onCalculate={handleCalculateIndoor}
          />
        )}

        {activeTab === 'transport' && (
          <EcoCommutePlanner
            comparison={routeComparison}
            loading={loadingTransport}
            onCompare={handleCompareRoutes}
          />
        )}

        {activeTab === 'community' && (
          <CommunityHazardMap
            reports={communityReports}
            loading={loadingCommunity}
            userLat={currentCity.lat}
            userLon={currentCity.lon}
            onSubmitReport={handleSubmitReport}
            onUpvote={handleUpvoteReport}
          />
        )}
      </main>

      {/* Floating AI Assistant Drawer */}
      <AICopilotDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        messages={chatMessages}
        loading={chatLoading}
        onSendMessage={handleSendMessage}
        currentAQI={currentAQI?.aqi_us || 50}
        sensitivity={sensitivity}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>
            AirGuard AI — Urban Environmental Intelligence Platform • Built for Hack2Skill PromptWars
          </p>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Powered by Open-Meteo & Gemini</span>
            <span>•</span>
            <span className="text-teal-400">Zero Fabricated Data Guarantee</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
