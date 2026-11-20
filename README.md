# AirGuard AI 🌍🛡️

**Urban Air Quality Assistant & Environmental Intelligence Platform**  
*Hack2Skill PromptWars Submission*

AirGuard AI is a real-world environmental intelligence platform delivering location-based air quality intelligence, personalized physiological risk mitigation, sustainable transport calculations, community pollution hazard reporting, and context-grounded AI copilot assistance.

---

## 🚀 Key Features

1. **Hyper-Local AQI Intelligence**: Real-time US & European AQI, PM2.5, PM10, O3, NO2, SO2, CO, and UV Index with explicit **Data Provenance** (`OBSERVED`, `FORECAST`, `ESTIMATED`).
2. **24-Hour & 7-Day Forecasts**: Diurnal pollutant curve visualizations to pinpoint pollution inversion spikes and clean air windows.
3. **Personalized AI Daily Routines**: Tailored recommendations based on individual health sensitivities (Normal, Asthmatic, Elderly, Child, Athlete).
4. **Indoor Air Quality & Ventilation Advisor**: Optimal window opening times and HEPA purifier runtime guidance.
5. **Sustainable Transportation & Carbon Impact**: Multi-modal route comparison highlighting inhaled pollutant exposure vs. CO2 saved.
6. **Crowdsourced Community Hazard Reporting**: Geo-tagged reporting of industrial emissions, crop residue burning, and traffic dust with spatial clustering.
7. **Context-Grounded AI Assistant**: Multi-turn conversational copilot powered by Gemini / Groq with zero fabricated data.

---

## 🏗️ Technology Stack

- **Frontend**: React 18/19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, Leaflet
- **Backend**: Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), GeoAlchemy2
- **Database**: PostgreSQL with PostGIS (Neon Cloud) / SQLite local fallback
- **Environmental Data**: Open-Meteo Air Quality & Weather API
- **AI Engine**: Google Gemini 2.0 Flash / Groq Llama-3.3-70b / Deterministic Expert Engine fallback
- **Testing**: Pytest, Vitest

---

## 📁 Repository Structure

```text
AIRGUARD-AI/
├── backend/                # FastAPI application, services, and tests
│   ├── app/
│   │   ├── api/v1/         # REST API endpoints
│   │   ├── core/           # Configuration, security, logging
│   │   ├── db/             # Database session & models
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic v2 schemas
│   │   └── services/       # Open-Meteo, AI engine, calculation engines
│   └── tests/              # Pytest test suite
├── frontend/               # React + TypeScript + Vite frontend
│   └── src/
│       ├── components/     # UI, AQI, Forecast, Maps, Transport, Community, AI
│       ├── hooks/          # Custom React hooks
│       ├── services/       # API client & endpoints
│       └── stores/         # Zustand state management
├── docs/                   # Architecture and API documentation
└── .env.example            # Environment variable template
```

---

## ⚡ Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend API Docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend Application: `http://localhost:5173`

---

## 📜 License & Compliance

Designed and built for the Hack2Skill PromptWars Challenge. All environmental data sourced with clear provenance from open atmospheric modeling frameworks.
