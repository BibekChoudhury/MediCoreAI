# 📋 MediCore AI — Project Summary

## Overview

**MediCore AI** is a comprehensive medical intelligence platform that combines disease prediction, AI-powered health consultation, prescription analysis, health report analysis, and a dedicated Heart Health monitoring module — all unified under a single full-stack application.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (port 3000)                      │
│  React + Vite Frontend  ──  Vite Proxy (/api, /heart)           │
└──────────────┬───────────────────────┬──────────────────────────┘
               │                       │
               ▼                       ▼
┌──────────────────────────┬───────────────────────────────────────┐
│   MediCore Backend       │   Heart Health Sub-App                │
│   FastAPI (port 8000)    │   Mounted at /heart                   │
│                          │                                       │
│  • Auth (JWT)            │  • Cardia AI Chatbot (OpenRouter)     │
│  • Disease Prediction    │  • Cardiac Risk Prediction            │
│  • AI Consultation (Groq)│  • ECG Analysis                       │
│  • Prescription Analyzer │  • Angiography/Angioplasty Analysis   │
│  • Health Report Analyzer│  • Heart Sound Analysis               │
│  • Smart MedBuddy        │  • Real-time Vital Monitoring         │
│                          │  • Health Connect Data Sync            │
│  SQLite: medicore_auth.db│  SQLite: heart_health.db              │
└──────────────────────────┴───────────────────────────────────────┘
               │                       │
               ▼                       ▼
        Groq LLM API            OpenRouter API
        (llama-3-70b)           (Claude Opus 4.7)
```

### Technology Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | React 19, Vite 6, TailwindCSS 4    |
| Backend   | Python 3.13, FastAPI, Uvicorn       |
| Database  | SQLite (via SQLAlchemy ORM)         |
| ML Models | scikit-learn (Decision Tree)        |
| LLM (Main)| Groq API (Llama 3 70B)             |
| LLM (Heart)| OpenRouter (Claude Opus 4.7)       |
| Auth      | JWT (PyJWT + bcrypt)                |

---

## Project Structure

```
medicoreAI-main/
├── .env                          # Root env vars (GROQ_API_KEY, JWT secrets)
├── requirements.txt              # Python dependencies
├── start.md                      # Quick start guide
├── summary.md                    # This file
│
├── backend/                      # Main FastAPI backend
│   ├── main.py                   # App entry, routes, Heart module mount
│   ├── database.py               # SQLAlchemy DB setup
│   ├── middleware/
│   │   └── auth_middleware.py    # JWT auth middleware (bypasses /heart/)
│   ├── models/
│   │   └── user.py               # User, PatientProfile models
│   ├── controllers/
│   │   └── auth_controller.py    # Login, signup, profile logic
│   ├── routes/
│   │   └── auth_routes.py        # Auth API routes
│   ├── services/
│   │   ├── ai_service.py         # Groq LLM integration
│   │   ├── disease_service.py    # Disease prediction ML
│   │   ├── medicine_service.py   # Prescription OCR + analysis
│   │   ├── health_report_service.py # PDF/image report analysis
│   │   ├── alternative_service.py   # Medicine alternatives
│   │   ├── ocr_service.py        # Image-to-text extraction
│   │   └── personalization_engine.py # User profile personalization
│   └── utils/
│       └── security.py           # JWT encode/decode helpers
│
├── Heart/                        # Heart Health sub-application
│   ├── .env                      # Heart-specific env vars
│   ├── config.py                 # Configuration (reads .env)
│   ├── main.py                   # FastAPI sub-app entry
│   ├── api/v1/                   # API routes
│   │   ├── agent.py              # Cardia chatbot endpoint
│   │   ├── prediction.py         # Heart attack risk prediction
│   │   ├── ecg_analysis.py       # ECG report upload + analysis
│   │   ├── angiography_analysis.py # Angiography PDF analysis
│   │   ├── angioplasty_analysis.py # Angioplasty PDF analysis
│   │   ├── heart_sound.py        # Heart sound WAV analysis
│   │   ├── monitoring.py         # Real-time vital monitoring
│   │   ├── data_sources.py       # Health Connect sync + data submit
│   │   ├── watch.py              # Smartwatch data endpoints
│   │   └── auth.py               # Heart module auth
│   ├── services/
│   │   ├── llm_service.py        # OpenRouter LLM integration
│   │   ├── deep_agent.py         # Intent detection + orchestration
│   │   ├── jarvis_personality.py # Cardia personality + response gen
│   │   ├── prediction_service.py # ML heart attack prediction
│   │   ├── ecg_service.py        # ECG waveform analysis
│   │   ├── heart_sound_service.py # Audio processing (librosa)
│   │   ├── angioplasty_service.py # Angioplasty report parsing
│   │   ├── monitoring_service.py # Vital sign monitoring logic
│   │   ├── alert_service.py      # Threshold alerts
│   │   ├── context_engine.py     # Conversational context
│   │   ├── watch_service.py      # Watch data management
│   │   └── voice_service.py      # TTS service
│   ├── models/                   # SQLAlchemy models
│   ├── static/dashboard/         # Frontend dashboard
│   │   ├── index.html            # Dashboard HTML
│   │   ├── css/styles.css        # Futuristic dark theme CSS
│   │   └── js/app.js             # Dashboard JavaScript
│   └── datasets/                 # Training data
│
└── MEDI_CORE_ASSIST/frontend/    # React frontend
    ├── vite.config.js            # Vite config + proxy (/api, /heart)
    ├── package.json              # Node dependencies
    └── src/
        ├── App.jsx               # Root component + routing
        ├── api/client.js         # API base URL helper
        └── pages/
            ├── Login.jsx             # Login page
            ├── Signup.jsx            # Registration page
            ├── DashboardHome.jsx     # Module selection dashboard
            ├── DashboardLayout.jsx   # Sidebar layout
            ├── DiseasePrediction.jsx # Symptom-based prediction
            ├── Consultation.jsx      # AI health consultation
            ├── Prescription.jsx      # Smart MedBuddy (Rx analysis)
            ├── HealthReportAnalyzer.jsx # Lab report analyzer
            └── HeartHealthModule.jsx # Heart dashboard (iframe)
```

---

## Module Details

### 1. Authentication System

- **JWT-based** authentication with login/signup
- Passwords hashed with **bcrypt**
- Token stored in `localStorage`, sent via `Authorization: Bearer` header
- Middleware bypasses `/heart/` routes (Heart has its own auth)

### 2. Disease Prediction (ML)

- **Model:** Decision Tree Classifier (scikit-learn)
- **Training Data:** 131 symptoms → 41 diseases
- **Input:** User selects symptoms from a checklist
- **Output:** Predicted disease with description, precautions, medications, diet, and workout recommendations
- **Files:** `backend/services/disease_service.py`, model at `backend/models/ml/`

### 3. AI Consultation (Groq LLM)

- **Provider:** Groq API (Llama 3 70B Versatile)
- **Features:**
  - Conversational health Q&A
  - Image analysis (upload medical images)
  - Voice input via browser Web Speech API
  - Text-to-speech output via browser SpeechSynthesis
- **Personalized** using patient profile (age, blood group, medications)
- **File:** `backend/services/ai_service.py`

### 4. Smart MedBuddy (Prescription Analyzer)

- **Upload** prescription photos or PDFs
- **OCR extraction** of medicine names (PyMuPDF for PDF, custom for images)
- **AI analysis** of each medicine: purpose, dosage, side effects
- **Alternative suggestions** for each medicine
- Extracted medicines auto-saved to patient profile
- **Files:** `backend/services/medicine_service.py`, `ocr_service.py`

### 5. Health Report Analyzer

- **Upload** lab reports (PDF or images)
- **Extracts** test values using Groq vision/text analysis
- **Interprets** results: normal ranges, flags abnormal values
- **Generates** a plain-language summary with actionable recommendations
- **File:** `backend/services/health_report_service.py`

### 6. Heart Health Module (Sub-Application)

The Heart Health module is a **standalone FastAPI application** mounted at `/heart` within the main backend. It has its own database, services, and a full dashboard UI.

#### 6a. Cardia AI Chatbot

- **LLM Provider:** OpenRouter (Claude Opus 4.7)
- **Intent Detection:** Greeting, vitals monitoring, risk assessment, report analysis, device management
- **Orchestrator:** `DeepAgent` routes intents to specialized services
- **Personality Engine:** `JarvisPersonality` generates contextual, warm responses
- **Context Engine:** Maintains conversation history per user
- **Files:** `Heart/services/deep_agent.py`, `llm_service.py`, `jarvis_personality.py`

#### 6b. Cardiac Risk Prediction

- **ML Model:** Decision Tree (trained on heart attack dataset)
- **Input:** Age, sex, cholesterol, blood pressure, blood sugar, ECG type, max heart rate, exercise angina, etc.
- **Output:** Risk percentage, risk level (Low/Moderate/High/Critical), contributing factors, health tips
- **File:** `Heart/services/prediction_service.py`

#### 6c. ECG Analysis

- **Upload** ECG report images
- **AI-powered** analysis via OpenRouter LLM
- Identifies: rhythm, intervals, ST segment changes, axis deviation
- **File:** `Heart/services/ecg_service.py`

#### 6d. Angiography & Angioplasty Report Analysis

- **Upload** PDF reports
- **Extracts** vessel blockages, stent placements, LVEF, recommendations
- Uses PyMuPDF for text extraction + LLM for interpretation
- **Files:** `Heart/services/angioplasty_service.py`, `Heart/api/v1/angiography_analysis.py`

#### 6e. Heart Sound Analysis

- **Upload** WAV audio of heart sounds
- **Processes** with librosa: spectral features, MFCC, zero-crossing rate
- Detects: murmurs, arrhythmias, normal/abnormal patterns
- **File:** `Heart/services/heart_sound_service.py`

#### 6f. Real-time Vital Monitoring

- **Monitors** heart rate, SpO2, HRV, blood pressure, steps
- **Data sources:** Android Health Connect (via companion app), manual entry
- **Auto-sync** every 2 seconds in the dashboard
- **Alert system:** configurable thresholds for abnormal readings
- **Backward compat:** Old paths (`/api/v1/data/health/submit`) redirect to `/heart/...`
- **Files:** `Heart/services/monitoring_service.py`, `Heart/api/v1/data_sources.py`

#### 6g. Dashboard UI

- **Futuristic dark theme** with neon glow effects, glassmorphism
- **4 tabs:** Dashboard (vitals + charts), Risk Scan (prediction form), Reports (upload ECG/angiography/heart sounds), Devices (connect wearables)
- **Chart.js** for real-time vital trend charts
- **Responsive** design, embedded via iframe in the React frontend
- **Files:** `Heart/static/dashboard/index.html`, `css/styles.css`, `js/app.js`

---

## Data Flow

### Disease Prediction Flow
```
User selects symptoms → POST /api/predict
→ disease_service.py → ML model inference
→ Returns: disease, description, precautions, medications, diet, workout
```

### AI Consultation Flow
```
User types/speaks query → POST /api/consultation
→ ai_service.py → Groq LLM (with patient profile context)
→ Returns: AI response (text) → Browser TTS speaks it
```

### Heart Health - Cardia Chat Flow
```
User message → POST /heart/api/v1/agent/command
→ deep_agent.py (intent detection)
→ Routes to: monitoring_service / prediction_service / ecg_service / etc.
→ Gathers health data → jarvis_personality.py (builds LLM prompt)
→ llm_service.py → OpenRouter (Claude) → Contextual response
→ Returns: response, suggestions, emotional_tone
```

### Health Connect Sync Flow
```
Android App (Health Connect) → POST /api/v1/data/health/submit
→ auth_middleware.py (bypassed — public path)
→ Redirected (307) → /heart/api/v1/data/health/submit
→ data_sources.py → Stores in heart_health.db
→ Dashboard auto-syncs every 2s via /heart/api/v1/data/sync/all
```

---

## API Endpoints

### Main Backend (`/api/...`)

| Method | Path                    | Description                     |
|--------|-------------------------|---------------------------------|
| POST   | `/api/auth/signup`      | User registration               |
| POST   | `/api/auth/login`       | User login (returns JWT)        |
| GET    | `/profile`              | Get user profile                |
| PUT    | `/profile`              | Update user profile             |
| POST   | `/api/predict`          | Disease prediction              |
| POST   | `/api/consultation`     | AI health consultation          |
| GET    | `/api/symptoms`         | Get all symptom names           |
| GET    | `/api/metadata`         | Get model metadata              |
| POST   | `/upload-prescriptions` | Upload & analyze prescription   |
| POST   | `/api/analyze-report`   | Analyze health report           |
| GET    | `/health`               | Backend health check            |

### Heart Module (`/heart/api/v1/...`)

| Method | Path                              | Description                      |
|--------|-----------------------------------|----------------------------------|
| POST   | `/heart/api/v1/agent/command`     | Cardia AI chatbot                |
| POST   | `/heart/api/v1/predict`           | Heart attack risk prediction     |
| POST   | `/heart/api/v1/ecg/analyze`       | ECG report analysis              |
| POST   | `/heart/api/v1/angiography/analyze` | Angiography PDF analysis       |
| POST   | `/heart/api/v1/angioplasty/analyze` | Angioplasty PDF analysis       |
| POST   | `/heart/api/v1/heart-sound/analyze`| Heart sound WAV analysis        |
| POST   | `/heart/api/v1/data/sync/all`     | Sync all data sources            |
| POST   | `/heart/api/v1/data/health/submit`| Receive Health Connect data      |
| GET    | `/heart/api/v1/monitoring/vitals` | Get latest vitals                |
| GET    | `/heart/api/v1/monitoring/stream` | SSE vital stream                 |

---

## Environment Variables Reference

### Root `.env`

| Variable                   | Required | Description                              |
|----------------------------|----------|------------------------------------------|
| `GROQ_API_KEY`             | Yes      | Groq API key for main AI features        |
| `JWT_SECRET_KEY`           | Yes      | JWT signing secret                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No   | Token expiry (default: 60)               |

### `Heart/.env`

| Variable              | Required | Description                                |
|-----------------------|----------|--------------------------------------------|
| `OPENROUTER_API_KEY`  | Yes      | OpenRouter key for Cardia chatbot          |
| `OPENROUTER_MODEL`    | No       | LLM model (default: llama-3.1-8b:free)    |
| `SECRET_KEY`          | Yes      | JWT secret for Heart module                |
| `DATABASE_URL`        | No       | Database URL (default: SQLite)             |
| `ELEVENLABS_API_KEY`  | No       | ElevenLabs TTS (optional, browser TTS used)|
| `GOOGLE_FIT_CLIENT_ID`| No      | Google Fit OAuth (optional)                |

---

## Key Integration Points

### Heart Module Mounting

The Heart sub-app is dynamically imported and mounted at `/heart` in `backend/main.py` (lines 108–152):
- Saves/restores `sys.path` and `sys.modules` to prevent namespace collisions
- Changes working directory to `Heart/` for correct `.env` loading
- Restores everything after mount

### Vite Proxy Configuration

`MEDI_CORE_ASSIST/frontend/vite.config.js` proxies:
- `/api/*` → `http://127.0.0.1:8000` (main backend)
- `/heart/*` → `http://127.0.0.1:8000` (Heart sub-app, including WebSocket)

### JWT Auth Middleware

`backend/middleware/auth_middleware.py` protects `/api/*` routes but allows:
- `/heart/*` — Heart sub-app has its own authentication
- `/api/v1/data/health/submit` — Health Connect redirect (public)
- Standard public paths: `/health`, `/login`, `/register`, `/docs`

---

## Databases

### `backend/medicore_auth.db`
- **users** — id, email, hashed_password, created_at
- **patient_profiles** — age, blood_group, weight, gender, medications, allergies

### `Heart/heart_health.db`
- **users** — Heart module user accounts
- **watch_data** — Vital readings (heart_rate, spo2, hrv, steps, blood_pressure, source, timestamp)
- **predictions** — Heart attack risk prediction history
- **alert_configs** — Custom vital threshold alerts
- **reports** — Uploaded report analysis history
