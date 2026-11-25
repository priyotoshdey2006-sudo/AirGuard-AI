# AirGuard AI — Production Deployment Guide

This guide details the step-by-step production deployment procedures for **AirGuard AI**.

```
+---------------------------------------+
|          AirGuard AI Frontend         |
|        Vercel (React + Vite SPA)      |
+-------------------+-------------------+
                    |
                    | HTTPS / JSON (VITE_API_BASE_URL)
                    v
+---------------------------------------+
|          AirGuard AI Backend          |
|      Render (FastAPI / Uvicorn)       |
+-------------------+-------------------+
                    |
                    | PostgreSQL + PostGIS Protocol (asyncpg / psycopg2)
                    v
+---------------------------------------+
|          Production Database          |
|    PostgreSQL 15+ with PostGIS 3.x    |
|   (Supabase / Neon / Render Postgres) |
+---------------------------------------+
```

---

## 1. Database Provisioning & PostGIS Requirement

### Strict Technical Requirement
AirGuard AI uses spatial indexing (GiST functional index on `cast(geom as geography)`) and spatial operators (`ST_DWithin`, `ST_Distance`) for 50 km radius AQI caching, nearby community pollution report clustering, and health diagnostic checks (`SELECT PostGIS_Version()`).
**Production strictly requires PostgreSQL with the PostGIS extension.** SQLite cannot be used in production; the backend will actively abort startup if `ENVIRONMENT=production` and `DATABASE_URL` starts with `sqlite`.

### Recommended Providers & Free-Tier Trade-offs

| Database Provider | PostGIS Support | Free-Tier Limits & Behavior | Recommendation |
| :--- | :--- | :--- | :--- |
| **Supabase** | Pre-installed (`CREATE EXTENSION postgis;`) | 500 MB storage, pauses after 1 week of inactivity (unpauses instantly) | **Strongly Recommended** for hackathons & production prototypes. |
| **Neon** | Supported via SQL command | 0.5 GiB storage, serverless autoscaling | **Recommended** alternative. |
| **Render Managed PostgreSQL** | Available | Free instance expires after 30 days and will be terminated | Use only with Paid Starter plan ($7/mo) for persistent production. |

### Provisioning Steps (Example: Supabase)
1. Log in to [Supabase](https://supabase.com) and click **New Project**.
2. Set a secure database password (save this securely).
3. Navigate to the **SQL Editor** in the Supabase Dashboard and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   SELECT PostGIS_Version();
   ```
4. Navigate to **Project Settings** -> **Database** -> **Connection string** -> **URI**.
5. Copy the connection URI. Change the protocol prefix from `postgresql://` to `postgresql+asyncpg://` and append `?ssl=require`:
   ```
   postgresql+asyncpg://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?ssl=require
   ```

---

## 2. Backend Deployment on Render

### Overview
- **Service Type**: Web Service
- **Environment**: Python 3
- **Root Directory**: `backend`
- **Port**: Render automatically provisions `$PORT`. The application binds dynamically.

### Step-by-Step Configuration
1. Log in to [Render](https://dashboard.render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (`AIRGUARD-AI`).
4. Configure service parameters:
   - **Name**: `airguard-ai-api` (or preferred name)
   - **Region**: Select closest to your users (e.g., Frankfurt, Oregon, Singapore)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free (or Starter)

5. Configure **Health Check Path**:
   - In **Advanced Settings**, set **Health Check Path** to `/health`.

6. Configure **Environment Variables** (in Render Dashboard -> Environment):

| Variable Name | Required | Example / Format | Notes |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | **Yes** | `production` | Enforces production security validations. |
| `SECRET_KEY` | **Yes** | *(64-character random hex)* | Must be >= 32 characters. Generate with `openssl rand -hex 32`. Insecure placeholders will fail startup. |
| `DATABASE_URL` | **Yes** | `postgresql+asyncpg://...` | Connection URI from Supabase/Neon with PostGIS. Must use `postgresql+asyncpg://` protocol and SSL. |
| `BACKEND_CORS_ORIGINS` | **Yes** | `https://airguard-ai.vercel.app` | Comma-separated list or JSON array of allowed origins. Add your Vercel URL once assigned. |
| `GEMINI_API_KEY` | Optional | `AIzaSy...` | Required for Gemini AI Copilot features. Falls back gracefully to deterministic health rules if omitted. |
| `GROQ_API_KEY` | Optional | `gsk_...` | Alternative high-speed LLM provider for Copilot. |
| `DEFAULT_AI_PROVIDER` | Optional | `gemini` | `gemini` or `groq`. |
| `RATE_LIMIT_PER_MINUTE` | Optional | `60` | Sliding window rate limit per client IP. |
| `AQI_CACHE_TTL_SECONDS`| Optional | `1800` | Atmospheric cache TTL (30 minutes default). |

7. Click **Create Web Service**.
8. Observe the Render deployment logs. The build will install packages, run Alembic migrations (`001_initial` -> `002_spatial` -> `003_functional_geog_index`), and start Uvicorn.
9. Note your assigned backend URL: `https://<your-render-app-name>.onrender.com`.

---

## 3. Frontend Deployment on Vercel

### Overview
- **Framework Preset**: `Vite`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Routing Configuration**: Handled via `frontend/vercel.json` (SPA route rewrites).

### Step-by-Step Configuration
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository (`AIRGUARD-AI`).
4. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click `Edit` and select `frontend`.
   - **Build and Output Settings**:
     - Build Command: `npm run build` (default)
     - Output Directory: `dist` (default)
     - Install Command: `npm install` (default)
5. Configure **Environment Variables**:
   - Add the following variable:
     - **Name**: `VITE_API_BASE_URL`
     - **Value**: `https://<your-render-app-name>.onrender.com` (your deployed Render backend URL, without trailing slash)
6. Click **Deploy**.
7. Vercel will install dependencies, run TypeScript validation (`tsc -b`), build Vite static assets, and deploy globally across the Edge Network.
8. Note your assigned Vercel production URL: `https://<your-app>.vercel.app`.

---

## 4. Post-Deployment Configuration & Smoke Testing

### Step 1: Align CORS on Backend
Once Vercel generates your production domain:
1. Return to the **Render Dashboard** -> `airguard-ai-api` -> **Environment**.
2. Update `BACKEND_CORS_ORIGINS`:
   ```
   BACKEND_CORS_ORIGINS=https://<your-app>.vercel.app,http://localhost:5173
   ```
3. Save changes. Render will automatically redeploy the service with the updated CORS policy.

### Step 2: Smoke Test Verification
Execute the following verification checklist:

1. **System Liveness Check**:
   ```bash
   curl -I https://<your-render-app>.onrender.com/health
   # Expected: HTTP 200 OK {"status": "healthy"}
   ```

2. **Database & PostGIS Readiness Probe**:
   ```bash
   curl https://<your-render-app>.onrender.com/api/v1/health
   # Expected: {"status": "healthy", "database": {"connected": true, "postgis_installed": true, "postgis_version": "..."}}
   ```

3. **Frontend Application Access**:
   - Open `https://<your-app>.vercel.app` in your browser.
   - Verify the Liquid Glass UI loads cleanly with no console CORS errors.
   - Test location selection (e.g., Delhi, London, New York) and verify live AQI cards populate.
   - Direct-refresh test: Refresh on `/forecast` and `/planner` to confirm `vercel.json` SPA routing rewrites work properly without 404 errors.
   - AI Copilot: Open the Copilot drawer, type a query, and verify real-time environmental context responses.

---

## 5. Troubleshooting & Operational Notes

- **Render Cold Starts on Free Tier**:
  Render free web services spin down after 15 minutes of inactivity. The first request after spindown may take 30-50 seconds. The frontend features an interactive loading state and error handling to accommodate this.
- **PostGIS Not Installed Error**:
  If the health check returns `"postgis_installed": false`, ensure you executed `CREATE EXTENSION postgis;` in your PostgreSQL instance before running Alembic migrations.
- **CORS Blocked**:
  If frontend requests fail with a browser CORS error, check that `BACKEND_CORS_ORIGINS` in Render matches the exact Vercel frontend URL, including the `https://` protocol and omitting trailing slashes.
