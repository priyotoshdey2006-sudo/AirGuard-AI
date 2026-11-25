# AirGuard AI — Product Modules Specification

This document provides a detailed breakdown of the 9 core modules of **AirGuard AI**, engineered for Hack2Skill PromptWars (Challenge 6: Urban Air Quality Assistant).

---

## Module Index

| # | Module Name | Route | Key Technologies | Scientific / Engineering Grounding |
|---|-------------|-------|------------------|------------------------------------|
| 1 | **Air Quality Dashboard** | `/` | React, Tailwind, Lucide | CPCB NAQI, US EPA AQI, WHO 2021 Benchmark, ECMWF CAMS |
| 2 | **Location Search & Pollution Hazard Map** | `/map` | Leaflet, OpenStreetMap, PostGIS | PostGIS ST_DWithin geospatial querying, crowd validation |
| 3 | **Pollution Forecast** | `/forecast` | Recharts, Open-Meteo API | 24-hour diurnal atmospheric model curves, temporal resampling |
| 4 | **AI Environmental Advisor Copilot** | `/advisor` / Drawer | Gemini / LLM engine, Context injection | Grounded in retrieved atmospheric metrics; Zero-Fabrication |
| 5 | **Personalized Daily Routine Planner** | `/planner` | Pydantic v2, Custom Scheduler | Diurnal minimum exposure windows, health sensitivity profiles |
| 6 | **Indoor Air Quality Guide** | `/indoor` | Mass-balance box model | Single-zone envelope infiltration, CADR, ACH calculation |
| 7 | **Sustainable Alternatives / Eco-Commute** | `/transport` | Impact Calculator, Geodesic math | Modal carbon comparison (IPCC factors), inhaled ventilation dose |
| 8 | **Environmental Impact Tracker** | `/impact` | Recharts, Simulation Engine | Cumulative avoided PM2.5 dose, tree carbon sequestration eq. |
| 9 | **About & Developer Information** | `/about` | React, Technical Architecture | Data provenance pledge, regulatory notices, system specs |

---

## Detailed Module Specifications

### Module 1: Air Quality Dashboard (`/`)
- **Objective:** Immediate, high-contrast situational awareness for urban residents and families.
- **Key Features:**
  - Real-time dual AQI display: CPCB Indian National AQI (0–500) and US EPA AQI (0–500).
  - Prominent categorical badge (Good, Satisfactory, Moderate, Poor, Very Poor, Severe).
  - Complete 6-pollutant breakdown: $PM_{2.5}$, $PM_{10}$, $NO_2$, $O_3$, $SO_2$, $CO$, plus UV Index.
  - Clinical comparison against WHO 2021 Global Air Quality Guidelines ($PM_{2.5}$ 24-hour level: 15 µg/m³).
  - Provenance transparency panel documenting model origin (ECMWF CAMS 0.4° grid) and cycle timestamps.

### Module 2: Location Search and Pollution Hazard Map (`/map`)
- **Objective:** Hyperlocal crowd-verified hazard awareness and spatial monitoring.
- **Key Features:**
  - Interactive Leaflet map centered on selected urban centers (Delhi, Mumbai, London, New York, Beijing, Tokyo).
  - Spatial radius querying backed by PostGIS `ST_DWithin` on geography coordinates.
  - Community incident reporting categories: Open Garbage Burning, Industrial Emissions, Construction Dust, Crop/Biomass Burning, Vehicular Smog.
  - Peer verification mechanism: Upvoting system to confirm active hazards.

### Module 3: Pollution Forecast (`/forecast`)
- **Objective:** 24-hour predictive planning to avoid exposure during diurnal smog peaks.
- **Key Features:**
  - Recharts area and line charts plotting 24-hour projected $PM_{2.5}$ and AQI curves.
  - Identifies diurnal thermal inversion peaks (typically 04:00–08:00 and 20:00–23:00).
  - Highlights safe ventilation and outdoor exercise windows when atmospheric boundary layer mixing is highest (typically 12:00–16:00).

### Module 4: AI Environmental Advisor Copilot (`/advisor` / Drawer)
- **Objective:** Natural language consultation for health risk, mask selection, and vulnerable family members.
- **Key Features:**
  - Provider-independent LLM backend (Gemini 2.0 / Groq / Fallback rule engine).
  - Strict context grounding: LLM system prompt is injected with real-time $PM_{2.5}$, CPCB index, and user sensitivity profile.
  - Enforced Zero-Fabrication Policy: Refuses to hallucinate measurements or predict ungrounded safety levels.
  - Actionable advice: Certified N95/FFP2 respirator fit guidance, eye irritation mitigation, vulnerable group care.

### Module 5: Personalized Daily Routine Planner (`/planner`)
- **Objective:** Health-customized daily activity optimization based on respiratory sensitivity.
- **Key Features:**
  - Six sensitivity tiers: General Public, Asthmatic, Cardiovascular, Elderly, Child, Outdoor Athlete.
  - Dynamic scheduling for user-selected activities (Morning Jog, Commute, School Run, Outdoor Sport, Evening Stroll).
  - Time-slotted recommendations with safety ratings (SAFE, CAUTION, AVOID) and specific protective gear requirements.

### Module 6: Indoor Air Quality Guide (`/indoor`)
- **Objective:** Physical modeling of indoor pollutant infiltration and air purifier sizing.
- **Key Features:**
  - Single-zone mass-balance physical screening model ($V \frac{dC_{in}}{dt} = P \cdot a \cdot V \cdot C_{out} - (a + k) V C_{in} - CADR \cdot C_{in}$).
  - Computes equivalent Air Changes per Hour (ACH = CADR / Room Volume).
  - Safe natural ventilation schedule: Recommends specific hour windows when outdoor air quality permits window opening.
  - Air purifier runtime optimization and filter maintenance guidance.

### Module 7: Sustainable Alternatives / Eco-Commute (`/transport`)
- **Objective:** Encourage low-emission, low-exposure urban transportation.
- **Key Features:**
  - Compares 6 transit options: Metro Rail, Electric Bus, Bicycle/Walking, Electric Vehicle (EV), Carpool, and ICE Private Car.
  - Inhaled respiratory dose index calculated from minute ventilation rate (L/min) multiplied by exposure duration.
  - Carbon footprint differential ($kg\ CO_2$ generated and saved vs standard petrol/diesel vehicles).

### Module 8: Environmental Impact Tracker (`/impact`)
- **Objective:** Quantify long-term citizen contributions and avoided health hazards.
- **Key Features:**
  - Cumulative avoided inhaled $PM_{2.5}$ particulate dose (milligrams avoided from lungs via N95 + HEPA).
  - Equivalent avoided cigarette toxicity (based on Berkeley Earth 22 µg/m³ 24h equivalence).
  - Carbon offset metrics: Annual projected $kg\ CO_2$ saved and equivalent mature tree-absorption years.
  - Interactive lifestyle simulator with sliders for distance, clean transit days, mask compliance, and purifier runtime.

### Module 9: About & Developer Information (`/about`)
- **Objective:** Complete transparency, regulatory disclaimers, and open architecture.
- **Key Features:**
  - Detailed overview of Hack2Skill Challenge 6 requirements and design rationale.
  - Explicit data provenance pledge and regulatory distinction between model proxies and statutory CAAQMS monitors.
  - Documentation of open-source libraries, APIs, and architectural specifications.
