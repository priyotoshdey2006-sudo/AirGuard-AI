# AirGuard AI 🌍🛡️

**Urban Air Quality Assistant & Environmental Intelligence Platform**  
*Hack2Skill PromptWars — Challenge 6: Urban Air Quality Assistant*

AirGuard AI is a real-world, professionally engineered environmental intelligence platform designed to protect families and urban communities during severe winter smog episodes, optimize daily routines based on diurnal atmospheric curves, estimate indoor air quality via physical mass-balance modeling, and guide sustainable urban mobility choices.

---

## 🎯 Hack2Skill Challenge 6: Key Highlights

- **Real, Functional Application**: Complete, end-to-end full-stack platform with no mock data, no static demonstration pages, and no generic chatbot wrappers.
- **Zero-Fabrication Data Guarantee**: All environmental readings originate strictly from verified atmospheric models (ECMWF CAMS Global IFS-AER via Open-Meteo) or live public telemetry. If upstream data is unavailable, the system fails safely with RFC 7807 error responses rather than generating synthetic metrics.
- **Scientific Grounding**:
  - **Indian CPCB NAQI**: Piece-wise linear interpolation across 6 criteria pollutants ($PM_{2.5}$, $PM_{10}$, $NO_2$, $O_3$, $SO_2$, $CO$) with strict $\ge 3$ pollutant eligibility rules.
  - **US EPA AQI**: 2024 revised standard breakpoints.
  - **WHO 2021 Benchmarks**: Direct comparison against WHO daily health guideline levels ($PM_{2.5}$ 15 µg/m³).
  - **Single-Zone Mass-Balance Indoor Model**: Engineering screening estimating infiltration, indoor deposition, and Clean Air Delivery Rate (CADR) equivalent Air Changes per Hour (ACH).
  - **IPCC Commute Footprint**: Modal carbon calculations comparing electrified rail/metro against internal combustion engine vehicles.

---

## 🧭 The 9 Core Product Modules

| # | Module | Route | Description |
|---|--------|-------|-------------|
| 1 | **Air Quality Dashboard** | `/` | Dual CPCB/US EPA index gauges, 6 criteria pollutants, WHO health benchmarks, and data provenance audit panel. |
| 2 | **Location Search & Hazard Map** | `/map` | Interactive Leaflet GIS map with PostGIS spatial radius querying and crowd-validated incident reporting. |
| 3 | **Pollution Forecast** | `/forecast` | 24-hour diurnal atmospheric model projection highlighting nocturnal temperature inversion peaks and clean windows. |
| 4 | **AI Environmental Advisor** | `/advisor` / Drawer | Natural language copilot grounded in real-time atmospheric telemetry; advises on certified N95 respirators and vulnerable family care. |
| 5 | **Personalized Daily Planner** | `/planner` | Time-slotted schedule optimization across 6 health vulnerability profiles (Asthmatic, Elderly, Child, Athlete, etc.). |
| 6 | **Indoor Air Quality Guide** | `/indoor` | Physical box modeling of envelope infiltration, window ventilation windows, and CADR/ACH purifier runtime guidance. |
| 7 | **Eco-Commute Planner** | `/transport` | Multi-modal route comparisons calculating carbon footprints ($kg\ CO_2$) vs inhaled respiratory pollutant dose scores. |
| 8 | **Environmental Impact Tracker** | `/impact` | Long-term lifestyle impact simulator: cumulative avoided $PM_{2.5}$ inhaled dose, avoided cigarette toxicity, and tree-absorption equivalents. |
| 9 | **About & Data Architecture** | `/about` | Technical architecture breakdown, Open-Meteo & ECMWF data provenance pledge, and regulatory compliance notices. |

---

## 🏗️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, React Router v6, Lucide Icons, Recharts, Leaflet / React-Leaflet
- **Backend**: Python 3.12+, FastAPI (ASGI), Pydantic v2, SQLAlchemy 2.0 (async), GeoAlchemy2
- **Database**: PostgreSQL 16+ with PostGIS 3.x spatial extensions (with SQLite local development fallback)
- **External Atmospheric Data**: Open-Meteo Air Quality & Weather API (ECMWF CAMS Global 0.4° model)
- **AI Copilot**: Provider-independent LLM architecture (Google Gemini 2.0 Flash / Groq Llama-3.3-70b / Local deterministic expert engine)
- **CI / CD**: GitHub Actions (`.github/workflows/ci.yml`)

---

## 📁 Workspace Structure

```text
AIRGUARD-AI/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI (Backend tests + Frontend build)
├── backend/
│   ├── app/
│   │   ├── api/v1/              # REST API route handlers
│   │   │   ├── endpoints/       # aqi, indoor, recommendations, transport, community, assistant, health
│   │   │   └── router.py        # Central API v1 router
│   │   ├── core/                # Config, rate limiter, privacy logging, custom exceptions
│   │   ├── db/                  # SQLAlchemy async session, base models, migrations
│   │   ├── models/              # AQIRecord (PostGIS), CommunityReport, User
│   │   ├── schemas/             # Pydantic v2 request/response schemas
│   │   ├── services/            # CPCB/EPA calculators, indoor box model, Open-Meteo, AI engine
│   │   └── main.py              # FastAPI application entrypoint with root /health
│   ├── tests/                   # 54 backend unit and service tests
│   ├── alembic/                 # Database schema migrations
│   ├── requirements.txt         # Python backend dependencies
│   └── pytest.ini               # Pytest configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── aqi/             # Module 1: AQIDashboard
│   │   │   ├── community/       # Module 2: CommunityHazardMap
│   │   │   ├── forecast/        # Module 3: ForecastView
│   │   │   ├── assistant/       # Module 4: AICopilotDrawer
│   │   │   ├── recommendations/ # Module 5: DailyRoutinePlanner
│   │   │   ├── indoor/          # Module 6: IndoorAdvisor
│   │   │   ├── transport/       # Module 7: EcoCommutePlanner
│   │   │   ├── impact/          # Module 8: EnvironmentalImpactTracker
│   │   │   ├── about/           # Module 9: AboutPlatform
│   │   │   ├── common/          # Provenance badges and shared UI
│   │   │   └── layout/          # Sticky Navbar with React Router tabs
│   │   ├── services/            # Axios / fetch typed API client
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx              # React Router shell and global state
│   │   └── main.tsx             # React DOM root entrypoint
│   ├── package.json             # NPM dependencies (React, Vite, Tailwind, Recharts, Leaflet)
│   └── vite.config.ts           # Vite configuration
├── docs/
│   ├── ARCHITECTURE.md          # Architectural blueprints and mathematical formulas
│   ├── MODULES.md               # Deep-dive functional specifications for all 9 modules
│   └── API_REFERENCE.md         # Comprehensive REST API manual with request/response schemas
├── tests/
│   └── test_integration.py      # Root end-to-end integration smoke tests
├── docker-compose.yml           # Multi-container Docker deployment (FastAPI, PostGIS, Frontend)
├── .env.example                 # Documented environment variable template
├── .gitignore                   # Git exclusion rules
└── README.md                    # Project documentation
```

---

## ⚡ Quick Start & Local Execution

### Prerequisites
- Python 3.11, 3.12, or 3.14
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose for PostgreSQL + PostGIS

### 1. Backend Setup & Run

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

- **Root Status:** `http://localhost:8000/`
- **Liveness Probe:** `http://localhost:8000/health`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **OpenAPI Schema:** `http://localhost:8000/api/v1/openapi.json`

### 2. Frontend Setup & Run

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

- **Web Application:** `http://localhost:5173/`

### 3. Docker Deployment (Optional)

```bash
# Launch FastAPI backend, PostGIS spatial database, and React frontend
docker-compose up --build
```

---

## 🧪 Testing & Verification

AirGuard AI includes comprehensive automated test suites spanning unit calculators, database engines, rate limiters, and end-to-end integration workflows.

### Run All Backend & Integration Tests:
```bash
python -m pytest backend/tests tests/test_integration.py -v
```
**Status:** **61 passed, 2 skipped** (Live PostGIS tests safely skipped when PostgreSQL server is offline; run against local SQLite fallback).

### Run Frontend Production Typecheck & Build:
```bash
cd frontend
npm run build
```
**Status:** **Build succeeded** (`dist/index.html`, `dist/assets/*.js`, `dist/assets/*.css` compiled cleanly with 0 TypeScript errors).

---

## 🛡️ Data Provenance & Regulatory Notice

AirGuard AI displays atmospheric data derived from numerical weather prediction (ECMWF CAMS) and engineering box modeling. It is designed to assist personal and community health decisions during smog emergencies. It does not replace statutory regulatory reporting from continuous ambient air quality monitoring stations (CAAQMS) operated by environmental authorities.
