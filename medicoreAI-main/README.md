# MediCore AI — Intelligent Medical Assistant Platform

MediCore AI is a comprehensive, AI-powered healthcare platform that combines disease prediction, medical consultation, prescription analysis, health report interpretation, and cardiac health monitoring into a single unified application. It features a React-based frontend dashboard and a FastAPI backend with integrated machine learning models and third-party AI services.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Project](#running-the-project)
- [Modules & Functionality](#modules--functionality)
  - [Disease Prediction](#1-disease-prediction)
  - [AI Consultation](#2-ai-consultation)
  - [Prescription Analyzer (Smart MedBuddy)](#3-prescription-analyzer-smart-medbuddy)
  - [Health Report Analyzer](#4-health-report-analyzer)
  - [Heart Health Module](#5-heart-health-module)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [License](#license)

---

## Features

| Module | Description |
|---|---|
| **Disease Prediction** | ML-based symptom analysis using a trained Decision Tree model covering 40+ diseases |
| **AI Consultation** | Voice and image-based medical consultation powered by Groq LLM |
| **Prescription Analyzer** | OCR-based medicine extraction with generic alternatives and safety checks |
| **Health Report Analyzer** | Upload lab reports (PDF/image) for plain-language interpretation |
| **Heart Health Module** | Real-time cardiac monitoring, heart attack risk prediction, ECG/angiography/heart sound analysis, and Cardia AI chatbot |
| **Patient Profiles** | Personalized insights based on allergies, conditions, medications, and medical history |
| **Authentication** | JWT-based user authentication with session management |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│              (Vite + TailwindCSS)                    │
│        localhost:3000  →  proxy → :8000              │
│                                                      │
│  ┌──────────┬──────────┬──────────┬────────────────┐ │
│  │ Disease  │ AI       │ Prescr.  │ Heart Health   │ │
│  │ Predict  │ Consult  │ Analyzer │ (iframe embed) │ │
│  └──────────┴──────────┴──────────┴────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────┴──────────────────────────────┐
│              FastAPI Backend (port 8000)              │
│                                                      │
│  ┌─────────────────────┐  ┌────────────────────────┐ │
│  │  MediCore Main App  │  │  Heart Sub-App (/heart)│ │
│  │  ─ Auth & Profiles  │  │  ─ Heart Prediction    │ │
│  │  ─ Disease Predict  │  │  ─ ECG Analysis        │ │
│  │  ─ AI Consultation  │  │  ─ Angiography         │ │
│  │  ─ Prescription OCR │  │  ─ Heart Sound         │ │
│  │  ─ Health Reports   │  │  ─ Live Monitoring     │ │
│  │                     │  │  ─ Cardia AI Chatbot   │ │
│  │  SQLite (auth.db)   │  │  ─ Device Integration  │ │
│  └─────────────────────┘  │  SQLite (heart.db)     │ │
│                           └────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

The Heart Health Module is mounted as a FastAPI **sub-application** at the `/heart` prefix. This means:
- All Heart API endpoints are at `/heart/api/v1/...`
- The Heart dashboard is at `/heart/static/dashboard/index.html`
- Each module maintains its own database and auth system
- Everything runs on a single server process

---

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** SQLAlchemy + SQLite
- **ML:** scikit-learn, pandas, numpy, joblib
- **AI Services:** Groq API (vision + text), Featherless AI (LLM)
- **Auth:** JWT (PyJWT / python-jose), bcrypt
- **Audio:** librosa, soundfile, gTTS
- **PDF:** PyMuPDF (fitz)

### Frontend
- **Framework:** React 18 + Vite
- **Routing:** React Router v7
- **Styling:** TailwindCSS
- **UI:** Framer Motion, Lucide Icons
- **HTTP:** Axios

### Heart Health Dashboard
- **Type:** Standalone HTML/CSS/JS (embedded via iframe)
- **Charts:** Chart.js
- **Real-time:** WebSocket
- **AI Chat:** DeepAgent + Cardia personality engine

---

## Project Structure

```
medicoreAI-main/
├── backend/                    # MediCore main backend (FastAPI)
│   ├── main.py                 # App entry point + Heart sub-app mount
│   ├── database.py             # SQLAlchemy setup
│   ├── controllers/            # Business logic
│   │   ├── auth_controller.py
│   │   └── profile_controller.py
│   ├── routes/                 # API route definitions
│   │   ├── auth_routes.py
│   │   └── profile_routes.py
│   ├── models/                 # DB models & Pydantic schemas
│   │   ├── user.py
│   │   ├── patient_profile.py
│   │   ├── schemas.py
│   │   ├── auth_schemas.py
│   │   └── profile_schemas.py
│   ├── services/               # Service layer
│   │   ├── ai_service.py       # Groq AI integration
│   │   ├── disease_service.py  # Disease prediction ML
│   │   ├── medicine_service.py # Medicine extraction
│   │   ├── alternative_service.py
│   │   ├── ocr_service.py      # Prescription OCR
│   │   ├── health_report_service.py
│   │   └── personalization_engine.py
│   ├── middleware/
│   │   └── auth_middleware.py   # JWT auth middleware
│   └── utils/
│       ├── security.py         # Password hashing, JWT
│       ├── auth_dependencies.py
│       ├── patient_context.py
│       └── helpers.py
│
├── Heart/                      # Heart Health Module (sub-application)
│   ├── main.py                 # Heart FastAPI app
│   ├── config.py               # Environment-based config
│   ├── api/
│   │   ├── deps.py             # Auth dependencies
│   │   └── v1/                 # API v1 routes
│   │       ├── auth.py         # Heart auth (register/login)
│   │       ├── prediction.py   # Heart attack risk prediction
│   │       ├── monitoring.py   # Real-time vitals WebSocket
│   │       ├── ecg_analysis.py # ECG report analysis
│   │       ├── angioplasty_analysis.py
│   │       ├── heart_sound.py  # Heart sound classification
│   │       ├── agent.py        # Cardia AI chatbot
│   │       ├── data_sources.py # Device integration
│   │       └── watch.py        # Smartwatch data
│   ├── models/
│   │   ├── database.py         # Heart DB setup
│   │   ├── db_models.py        # ORM models
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── ml/
│   │       └── heart_attack_model.pkl
│   ├── services/
│   │   ├── auth_service.py     # JWT + bcrypt
│   │   ├── prediction_service.py
│   │   ├── monitoring_service.py
│   │   ├── ecg_service.py
│   │   ├── angioplasty_service.py
│   │   ├── heart_sound_service.py
│   │   ├── deep_agent.py       # DeepAgent orchestrator
│   │   ├── jarvis_personality.py # Cardia personality
│   │   ├── llm_service.py      # Featherless AI
│   │   ├── voice_service.py    # TTS (ElevenLabs)
│   │   ├── context_engine.py
│   │   ├── alert_service.py
│   │   └── watch_service.py
│   ├── static/dashboard/       # Heart dashboard UI
│   │   ├── index.html
│   │   ├── css/styles.css
│   │   └── js/app.js
│   ├── datasets/
│   │   └── heart_disease_cleaned.csv
│   └── requirements.txt
│
├── MEDI_CORE_ASSIST/           # Frontend + ML training
│   ├── frontend/               # React + Vite app
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── main.jsx
│   │   │   ├── index.css
│   │   │   ├── api/client.js   # Axios API client
│   │   │   ├── context/AuthContext.jsx
│   │   │   ├── pages/
│   │   │   │   ├── DashboardHome.jsx
│   │   │   │   ├── DashboardLayout.jsx
│   │   │   │   ├── DiseasePredictionPage.jsx
│   │   │   │   ├── Consultation.jsx
│   │   │   │   ├── Prescription.jsx
│   │   │   │   ├── HealthReportAnalyzer.jsx
│   │   │   │   ├── HeartHealthModule.jsx  ← NEW
│   │   │   │   ├── Login.jsx
│   │   │   │   └── Signup.jsx
│   │   │   └── components/
│   │   │       ├── Layout.jsx  # Sidebar + nav
│   │   │       ├── PrivateRoute.jsx
│   │   │       └── PublicRoute.jsx
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── models/                 # Trained ML models
│   │   ├── decision_tree_model_*.pkl
│   │   ├── label_encoder_*.pkl
│   │   └── model_metadata_*.json
│   ├── DATASET/                # Training datasets
│   └── notebook.ipynb          # Model training notebook
│
├── requirements.txt            # All Python dependencies
├── .gitignore
└── README.md                   # This file
```

---

## Setup & Installation

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18+ and **npm**
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd medicoreAI-main
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv_new
source venv_new/bin/activate      # macOS/Linux
# venv_new\Scripts\activate       # Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd MEDI_CORE_ASSIST/frontend
npm install
cd ../..
```

### 5. Configure Environment Variables

Create a `.env` file in the **project root** (or copy from `Heart/.env.example`):

```bash
cp Heart/.env.example .env
```

Edit the `.env` file and set:

```env
# Required for AI Consultation module
GROQ_API_KEY=your-groq-api-key

# Required for Heart Health AI features
FEATHERLESS_API_KEY=your-featherless-key
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
FEATHERLESS_MODEL=meta-llama/Llama-3-8B-Instruct

# JWT Secret (change in production)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Optional
ELEVENLABS_API_KEY=your-elevenlabs-key
GOOGLE_FIT_CLIENT_ID=your-client-id
GOOGLE_FIT_CLIENT_SECRET=your-client-secret
```

> **Note:** The Heart module loads its `.env` from the `Heart/` directory. The backend loads from the project root. Make sure both have the required variables.

---

## Running the Project

### Start the Backend Server

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

This starts both the MediCore backend **and** the Heart Health Module (auto-mounted at `/heart`).

#### Verify the backend is running:

| URL | What it shows |
|---|---|
| http://localhost:8000/health | MediCore health check |
| http://localhost:8000/docs | MediCore API documentation (Swagger) |
| http://localhost:8000/heart/ | Heart module root info |
| http://localhost:8000/heart/docs | Heart module API documentation |
| http://localhost:8000/heart/static/dashboard/index.html | Heart Health Dashboard |

### Start the Frontend Dev Server

In a **separate terminal**:

```bash
cd MEDI_CORE_ASSIST/frontend
npm run dev
```

The frontend will start at **http://localhost:3000**.

### Access the Application

1. Open **http://localhost:3000** in your browser
2. **Sign up** for a new account or **log in**
3. You'll see the **MediCore Dashboard** with all modules:
   - Disease Prediction
   - AI Consultation
   - Prescription Analyzer
   - Health Report Analyzer
   - **Heart Health Module** (opens the Cardia dashboard)

---

## Modules & Functionality

### 1. Disease Prediction

**Path:** `/dashboard/disease`

Uses a trained Decision Tree classifier to predict diseases based on symptoms.

- Select symptoms from a searchable list (130+ symptoms)
- Get top disease predictions with confidence scores
- View disease descriptions and precautions
- Personalized insights based on patient profile (allergies, medications)

**How it works:**
- The ML model was trained on a dataset of 4,920 records covering 41 diseases
- Features are binary symptom vectors
- Results include descriptions and precautionary measures

### 2. AI Consultation

**Path:** `/dashboard/consultation`

Real-time medical consultation powered by Groq's vision and language models.

- **Voice Input:** Speak your symptoms using the microphone
- **Image Upload:** Upload photos of skin conditions, injuries, etc.
- **Text-to-Speech:** Hear the AI's response read aloud
- **Combined Mode:** Voice + image for comprehensive analysis
- Personalized warnings based on patient allergies and conditions

**How it works:**
- Audio → Groq Whisper transcription → text query
- Image → Base64 encoding → Groq vision model analysis
- Responses are personalized using the patient's medical profile

### 3. Prescription Analyzer (Smart MedBuddy)

**Path:** `/dashboard/prescription`

Upload a prescription image/PDF to extract medicines and find alternatives.

- **OCR Extraction:** Reads medicine names from prescription images
- **Generic Alternatives:** Finds cost-effective generic equivalents
- **Safety Checks:** Cross-references with patient allergies and current medications
- **Auto-Profile Update:** Extracted medications are saved to the patient profile

**How it works:**
- Image/PDF → Groq vision model → raw text extraction
- Text → LLM parsing → structured medicine list (brand name, generic name)
- Each medicine → alternative lookup → safety cross-reference

### 4. Health Report Analyzer

**Path:** `/dashboard/health-analyzer`

Upload lab reports for plain-language interpretation.

- **Multi-format:** Supports PDF, JPG, PNG lab reports
- **Structured Analysis:** Breaks down blood panels, metabolic panels, etc.
- **Plain Language:** Explains results in easy-to-understand terms
- **Personalized Context:** Factors in existing conditions and medications

**How it works:**
- File upload → Groq vision extraction → raw report text
- Text → LLM analysis → structured interpretation with recommendations
- Results personalized based on patient profile

### 5. Heart Health Module

**Path:** `/dashboard/heart-health`

A comprehensive cardiac health platform with its own AI assistant, real-time monitoring, and multiple analysis tools.

#### 5a. Command Center Dashboard
- **Real-time Vitals:** Heart rate, SpO2, HRV, and step count with live charts
- **ECG Line Animation:** Visual heartbeat representation
- **WebSocket Monitoring:** Live data streaming from connected devices
- **Time Period Filter:** View data for today, 7 days, 30 days, or all time

#### 5b. Heart Attack Risk Prediction
- **13-parameter Input:** Age, sex, chest pain type, blood pressure, cholesterol, blood sugar, ECG, max heart rate, exercise angina, ST depression, slope, vessels, thalassemia
- **ML Model:** Trained classifier with risk score (0-100%), risk level (Low/Moderate/High/Critical)
- **Contributing Factors:** Interpretable factors with severity ratings
- **Cardia Narration:** AI-generated explanation of results

#### 5c. ECG Report Analysis
- Upload ECG images (JPEG/PNG), PDFs, or paste report text
- Keyword-based pattern recognition + LLM-enhanced explanation
- Identifies: arrhythmias, ST changes, axis deviation, conduction abnormalities
- Risk flags and follow-up recommendations

#### 5d. Angiography Report Analysis
- Upload angiography procedure reports (PDF)
- Extracts: stent details, artery locations, complications
- Provides plain-language explanation and follow-up instructions

#### 5e. Heart Sound Analysis
- Upload heart sound recordings (WAV/MP3, 10-60 seconds)
- Audio feature extraction (MFCC, spectral analysis)
- Classification: Normal, Murmur, Extra Sound, Artifact
- Confidence score and clinical explanation

#### 5f. Cardia AI Chatbot
- **Natural Language Interface:** Ask anything about your heart health
- **DeepAgent Orchestrator:** Routes queries to appropriate services
- **Voice Support:** Browser-native TTS for spoken responses
- **Context Awareness:** Remembers conversation history
- **Suggestions:** Smart follow-up question buttons

#### 5g. Connected Devices
- **Google Fit:** OAuth2 integration for Android phones/Wear OS
- **Health Connect:** Android app companion for real-time data sync
- **Manual Entry:** Log vitals manually (heart rate, blood pressure, SpO2)
- **Firebolt Watch / Fitbit:** Integration placeholders (coming soon)

---

## API Reference

### MediCore Main API (port 8000)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/health` | API health status |
| `POST` | `/register` | Register new user |
| `POST` | `/login` | Login (returns JWT) |
| `POST` | `/logout` | Logout |
| `GET` | `/profile` | Get user profile |
| `PUT` | `/profile` | Update profile |
| `GET` | `/api/symptoms` | List all symptoms |
| `GET` | `/api/metadata` | Model metadata |
| `POST` | `/api/predict` | Predict disease from symptoms |
| `GET` | `/api/disease-info` | All disease descriptions |
| `POST` | `/api/ai/image-analysis` | AI image analysis |
| `POST` | `/api/ai/transcribe` | Audio transcription |
| `POST` | `/api/ai/text-to-speech` | Text to speech |
| `POST` | `/api/ai/full-consultation` | Full AI consultation |
| `POST` | `/api/analyze` | Analyze prescription |
| `POST` | `/api/analyze-health-report` | Analyze health report |

### Heart Health API (mounted at `/heart`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/heart/` | Heart module info |
| `GET` | `/heart/docs` | Heart API documentation |
| `POST` | `/heart/api/v1/auth/register` | Register (Heart module) |
| `POST` | `/heart/api/v1/auth/login` | Login (Heart module) |
| `GET` | `/heart/api/v1/auth/me` | Current user info |
| `POST` | `/heart/api/v1/predict/heart-attack` | Heart attack risk prediction |
| `GET` | `/heart/api/v1/predict/history/{user_id}` | Prediction history |
| `WS` | `/heart/api/v1/monitor/live/{user_id}` | Live vitals WebSocket |
| `POST` | `/heart/api/v1/monitor/vitals` | Submit vitals |
| `GET` | `/heart/api/v1/monitor/latest/{user_id}` | Latest vitals |
| `GET` | `/heart/api/v1/monitor/trends/{user_id}` | Vitals trends |
| `GET` | `/heart/api/v1/monitor/history/{user_id}` | Vitals history |
| `GET` | `/heart/api/v1/monitor/summary/{user_id}` | Health summary |
| `POST` | `/heart/api/v1/monitor/alerts` | Create alert config |
| `POST` | `/heart/api/v1/analyze/ecg` | Analyze ECG report |
| `POST` | `/heart/api/v1/analyze/angiography/pdf` | Analyze angiography |
| `POST` | `/heart/api/v1/analyze/heart-sound` | Analyze heart sound |
| `WS` | `/heart/api/v1/agent/chat` | Cardia WebSocket chat |
| `POST` | `/heart/api/v1/agent/command` | Cardia text command |
| `POST` | `/heart/api/v1/agent/voice` | Voice command + TTS |
| `POST` | `/heart/api/v1/data/source/register` | Register data source |
| `GET` | `/heart/api/v1/data/sources/{user_id}` | List data sources |
| `POST` | `/heart/api/v1/data/manual` | Manual data entry |
| `POST` | `/heart/api/v1/data/health/submit` | Android Health Connect data |

---

## Environment Variables

### Backend (root `.env`)

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key for AI consultation, OCR, transcription |
| `JWT_SECRET_KEY` | Yes | Secret key for MediCore JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry (default: 60) |

### Heart Module (`Heart/.env`)

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | JWT secret for Heart module |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM features (get at openrouter.ai) |
| `OPENROUTER_BASE_URL` | No | OpenRouter API URL (default: https://openrouter.ai/api/v1) |
| `OPENROUTER_MODEL` | No | LLM model to use (default: meta-llama/llama-3.1-8b-instruct:free) |
| `DATABASE_URL` | No | Database URL (default: SQLite) |
| `PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Debug mode (default: true) |
| `ELEVENLABS_API_KEY` | No | ElevenLabs TTS API key |
| `GOOGLE_FIT_CLIENT_ID` | No | Google Fit OAuth client ID |
| `GOOGLE_FIT_CLIENT_SECRET` | No | Google Fit OAuth secret |
| `ALERT_EMAIL_ENABLED` | No | Enable email alerts (default: false) |

---

## License

This project is for educational purposes only. Always consult healthcare professionals for medical advice. The AI predictions and analyses provided by this platform are not a substitute for professional medical diagnosis or treatment.
