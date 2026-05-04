# Heart Health Module v2 - Comprehensive Documentation

> A sophisticated AI-powered heart health platform with DeepAgent orchestrator, JARVIS-like conversational interface, multi-source health data integration, and advanced diagnostic capabilities.

---

## Table of Contents
1. [Overview](#overview)
2. [Module Architecture](#module-architecture)
3. [Key Features](#key-features)
4. [Project Structure](#project-structure)
5. [Tech Stack](#tech-stack)
6. [Setup & Installation](#setup--installation)
7. [API Endpoints](#api-endpoints)
8. [Service Descriptions](#service-descriptions)
9. [Working Flow](#working-flow)
10. [Implementation Details](#implementation-details)
11. [Configuration](#configuration)

---

## Overview

The **Heart Health Module v2** is an intelligent cardiovascular health monitoring and diagnostic platform that leverages machine learning, natural language processing, and multi-source data integration. It provides:

- **Real-time Heart Disease Prediction** using ML models
- **ECG Analysis** with pattern recognition
- **Heart Sound Analysis** from audio recordings
- **Angioplasty Report Analysis** for procedure outcomes
- **Health Monitoring** with vital signs tracking
- **Conversational AI Interface (JARVIS)** powered by DeepAgent
- **Multi-Source Data Integration** (Google Fit, Fitbit, Firebolt, Manual Entry)
- **Intelligent Alerts & Monitoring** for abnormal patterns
- **User Authentication & Role-Based Access Control**

---

## Module Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Application                   │
│                    (main.py)                            │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┬─────────────────┐
        ↓                 ↓                 ↓
   ┌─────────┐    ┌──────────────┐    ┌────────┐
   │   API   │    │  WebSocket   │    │ Static │
   │ Routes  │    │  Chat (WS)   │    │ Files  │
   │ (REST)  │    │  (Real-time) │    │(Web UI)│
   └────┬────┘    └──────┬───────┘    └────────┘
        │                │
        └────────┬───────┘
                 ↓
        ┌─────────────────────┐
        │   DeepAgent         │
        │   Orchestrator      │
        │ (Intent Detection)  │
        └────────┬────────────┘
                 ↓
    ┌────────────────────────────────┐
    │    Service Layer               │
    │ ┌──────────────────────────┐  │
    │ │ • Prediction Service     │  │
    │ │ • Monitoring Service     │  │
    │ │ • ECG Service            │  │
    │ │ • Heart Sound Service    │  │
    │ │ • Angioplasty Service    │  │
    │ │ • Alert Service          │  │
    │ │ • LLM Service (Featherless) │
    │ │ • Voice Service (TTS)    │  │
    │ │ • Context Engine         │  │
    │ │ • Data Fusion Engine     │  │
    │ └──────────────────────────┘  │
    └────────────┬───────────────────┘
                 ↓
    ┌────────────────────────────────┐
    │   Data Sources                 │
    │ ┌──────────────────────────┐  │
    │ │ • Google Fit API         │  │
    │ │ • Fitbit API             │  │
    │ │ • Firebolt Database      │  │
    │ │ • Manual Entry           │  │
    │ │ • Uploaded Files (ECG)   │  │
    │ └──────────────────────────┘  │
    └────────────┬───────────────────┘
                 ↓
         ┌───────────────┐
         │  SQLite DB    │
         │  ML Models    │
         │  Uploads      │
         └───────────────┘
```

---

## Key Features

### 1. **Heart Attack Risk Prediction**
- Machine learning model trained on clinical datasets
- Features: Age, BP, Cholesterol, Max HR, ST depression, Slope, Vessels, Thalassemia
- Output: Risk score (0-100%) and risk classification (Low, Moderate, High, Critical)

### 2. **ECG Analysis**
- Image upload and analysis
- Pattern recognition (Normal, Abnormal, Borderline)
- QRS complex detection
- Heart rate estimation

### 3. **Heart Sound Analysis**
- MP3/WAV audio processing using Librosa
- Murmur detection
- S1/S2 heart sound splitting analysis
- Confidence scores for abnormalities

### 4. **Angioplasty Report Analysis**
- Procedural outcome assessment
- Stent placement verification
- Complication detection
- Recovery status tracking

### 5. **Real-Time Health Monitoring**
- Live vital signs (HR, BP, SpO2, Temp)
- Data aggregation from multiple sources
- Abnormality detection with automatic alerts
- Health trend analysis

### 6. **Conversational AI (JARVIS)**
- Intent-based routing (greeting, prediction, alerts, emergency, etc.)
- Emotional state detection
- Context-aware responses
- Multi-turn conversation history
- Voice synthesis with ElevenLabs TTS

### 7. **Multi-Source Data Integration**
- Google Fit API integration
- Fitbit API integration
- Firebolt data warehouse connection
- Manual entry support
- Data fusion and normalization

---

## Project Structure

```
Heart/
├── main.py                          # FastAPI application entry point
├── config.py                        # Environment configuration (Pydantic)
├── requirements.txt                 # Python dependencies
├── pyrightconfig.json               # Pyright type checking config
├── heart_health.db                  # SQLite database (auto-created)
│
├── api/
│   ├── __init__.py
│   ├── deps.py                      # Dependency injection (get_current_user, etc.)
│   └── v1/
│       ├── auth.py                  # Authentication endpoints (signup, login)
│       ├── prediction.py            # Heart attack prediction endpoint
│       ├── monitoring.py            # Vital signs monitoring endpoints
│       ├── ecg_analysis.py          # ECG analysis endpoints
│       ├── angioplasty_analysis.py  # Angioplasty report analysis
│       ├── heart_sound.py           # Heart sound analysis endpoints
│       ├── watch.py                 # Wearable device integration
│       ├── agent.py                 # DeepAgent/JARVIS chat endpoints (WebSocket)
│       └── data_sources.py          # Multi-source data integration endpoints
│
├── models/
│   ├── __init__.py
│   ├── database.py                  # SQLAlchemy ORM setup & db initialization
│   ├── db_models.py                 # ORM models (User, HealthRecord, Alert, etc.)
│   ├── schemas.py                   # Pydantic request/response schemas
│   └── ml/
│       └── heart_attack_model.pkl   # Trained ML model (scikit-learn)
│
├── services/
│   ├── __init__.py
│   ├── prediction_service.py        # ML model inference & risk scoring
│   ├── monitoring_service.py        # Vital signs aggregation & analysis
│   ├── ecg_service.py               # ECG image processing & analysis
│   ├── heart_sound_service.py       # Audio processing (Librosa)
│   ├── angioplasty_service.py       # Report analysis
│   ├── alert_service.py             # Alert detection & management
│   ├── llm_service.py               # Featherless AI integration (OpenAI-compatible)
│   ├── voice_service.py             # Text-to-speech (ElevenLabs)
│   ├── auth_service.py              # JWT token generation & validation
│   ├── context_engine.py            # Conversation context & intent detection
│   ├── deep_agent.py                # DeepAgent orchestrator (main AI logic)
│   ├── jarvis_personality.py        # JARVIS personality & response generation
│   ├── watch_service.py             # Wearable device data sync
│   └── data_sources/
│       ├── __init__.py
│       ├── base.py                  # Base DataSource class
│       ├── google_fit.py            # Google Fit API connector
│       ├── fitbit_connector.py      # Fitbit API connector
│       ├── firebolt.py              # Firebolt database connector
│       ├── manual_entry.py          # Manual health data entry
│       └── data_fusion.py           # Multi-source data aggregation
│
├── static/
│   └── dashboard/
│       ├── index.html               # Web dashboard UI
│       ├── css/
│       │   └── styles.css           # Styling
│       └── js/
│           └── script.js            # Frontend logic
│
├── datasets/
│   └── heart_disease_cleaned.csv    # Training dataset (UCI Heart Disease)
│
├── train/
│   └── train_model.py               # ML model training script
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py                  # API endpoint tests
│   └── test_llm.py                  # LLM service tests
│
├── uploads/
│   ├── ecg_*.jpg                    # ECG image uploads
│   └── heartsound_*.mp3             # Heart sound audio uploads
│
└── utils/
    └── __init__.py
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115+ |
| **Server** | Uvicorn 0.34+ |
| **Database** | SQLite + SQLAlchemy 2.0+ |
| **Auth** | JWT (python-jose), bcrypt |
| **ML/Data** | scikit-learn, pandas, numpy, joblib |
| **Audio** | Librosa, soundfile |
| **LLM** | Featherless AI (OpenAI-compatible) |
| **Voice** | ElevenLabs TTS API |
| **Testing** | pytest, httpx |
| **Config** | Pydantic BaseSettings, python-dotenv |

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- `pip` (Python package manager)
- 2GB disk space (for model + data)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Heart
```

### 2. Create Virtual Environment
```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///./heart_health.db

# Authentication
SECRET_KEY=your-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ML Model
ML_MODEL_PATH=./models/ml/heart_attack_model.pkl

# External APIs (Optional)
GOOGLE_FIT_CLIENT_ID=your-google-client-id
GOOGLE_FIT_CLIENT_SECRET=your-google-secret
FITBIT_CLIENT_ID=your-fitbit-id
FITBIT_CLIENT_SECRET=your-fitbit-secret

# LLM (Featherless AI)
FEATHERLESS_API_KEY=your-featherless-api-key
FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
FEATHERLESS_MODEL=meta-llama/Llama-3-8B-Instruct

# Voice/TTS
ELEVENLABS_API_KEY=your-elevenlabs-api-key
AZURE_SPEECH_KEY=your-azure-speech-key

# Alerts
ALERT_EMAIL_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### 5. Initialize Database
The database is auto-initialized on first run. To manually initialize:
```bash
python -c "from models.database import init_db; init_db()"
```

### 6. Run the Application
```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or via Python
python main.py
```

### 7. Access the Application
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Dashboard**: [http://localhost:8000/static/dashboard/index.html](http://localhost:8000/static/dashboard/index.html)
- **Root Endpoint**: [http://localhost:8000/](http://localhost:8000/)

---

## API Endpoints

### Authentication
```
POST   /api/v1/auth/signup           # Register new user
POST   /api/v1/auth/login            # Login (returns JWT token)
GET    /api/v1/auth/me               # Get current user info
POST   /api/v1/auth/refresh          # Refresh JWT token
```

### Heart Attack Prediction
```
POST   /api/v1/predict/heart-attack  # Predict risk (input: health metrics)
GET    /api/v1/predict/history/{userId}  # Get prediction history
```

### ECG Analysis
```
POST   /api/v1/analyze/ecg           # Upload & analyze ECG image
GET    /api/v1/analyze/ecg/{recordId}    # Get ECG analysis result
```

### Heart Sound Analysis
```
POST   /api/v1/analyze/heart-sound   # Upload & analyze heart sound audio
GET    /api/v1/analyze/heart-sound/{recordId}  # Get analysis result
```

### Angioplasty Analysis
```
POST   /api/v1/analyze/angioplasty   # Analyze angioplasty report
GET    /api/v1/analyze/angioplasty/{recordId}  # Get analysis result
```

### Health Monitoring
```
WS     /api/v1/monitor/live/{userId}     # WebSocket: Real-time vital signs
GET    /api/v1/monitor/history/{userId}  # Get historical vitals
POST   /api/v1/monitor/record-vitals     # Manual vital sign entry
```

### Data Sources
```
GET    /api/v1/data/sources/{userId}     # List connected data sources
POST   /api/v1/data/sources/connect      # Connect new data source (Google Fit, Fitbit)
GET    /api/v1/data/sync/{userId}        # Sync data from all sources
```

### DeepAgent / JARVIS Chat
```
WS     /api/v1/agent/chat                # WebSocket: Chat with JARVIS
POST   /api/v1/agent/chat/http           # HTTP: Single message (returns audio)
GET    /api/v1/agent/health              # Agent health status
```

### Wearable/Watch Integration
```
POST   /api/v1/watch/sync/{userId}       # Sync wearable device data
GET    /api/v1/watch/devices/{userId}    # Get connected devices
```

---

## Service Descriptions

### 1. **PredictionService** (`services/prediction_service.py`)
**Purpose**: ML-based heart disease risk assessment

**Functions**:
- `predict_heart_risk(input_data)` - Returns risk score and classification
- `get_prediction_history(user_id)` - Fetches past predictions
- `train_model()` - Retrains the ML model

**ML Features**:
- Age, Sex, Chest Pain Type, Resting BP, Cholesterol, Max HR, ST Depression, Slope, Number of Vessels, Thalassemia

**Output**: 
```json
{
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "confidence": 0.89,
  "recommendations": ["Consult cardiologist", "Reduce salt intake"]
}
```

### 2. **MonitoringService** (`services/monitoring_service.py`)
**Purpose**: Real-time vital signs tracking and aggregation

**Functions**:
- `get_latest_vitals(user_id)` - Current vital signs
- `record_vitals(user_id, vitals)` - Log new readings
- `generate_health_summary(user_id)` - Daily health report
- `detect_anomalies(user_id)` - Find abnormal patterns

**Vital Signs Tracked**:
- Heart Rate (bpm)
- Blood Pressure (sys/dia mmHg)
- SpO2 (%)
- Body Temperature (°C)
- Steps, Calories, Sleep Duration

### 3. **ECGService** (`services/ecg_service.py`)
**Purpose**: 12-lead ECG image analysis

**Functions**:
- `analyze_ecg_image(image_path)` - Image processing & pattern recognition
- `extract_features(image)` - QRS detection, wave identification
- `classify_ecg(features)` - Normal/Abnormal/Borderline classification

**Output**:
```json
{
  "status": "Abnormal",
  "heart_rate": 82,
  "findings": ["ST elevation in V1-V3", "Possible MI"],
  "confidence": 0.87
}
```

### 4. **HeartSoundService** (`services/heart_sound_service.py`)
**Purpose**: Cardiac auscultation audio analysis

**Functions**:
- `analyze_heart_sound(audio_path)` - Librosa spectral analysis
- `detect_murmurs(spectrogram)` - Abnormal sound detection
- `classify_heart_sounds(features)` - S1/S2 classification

**Output**:
```json
{
  "s1_detected": true,
  "s2_detected": true,
  "murmur_detected": true,
  "murmur_severity": "moderate",
  "confidence": 0.82
}
```

### 5. **AngioplastyService** (`services/angioplasty_service.py`)
**Purpose**: Post-angioplasty procedure analysis

**Functions**:
- `analyze_report(report_text)` - NLP-based outcome extraction
- `extract_key_metrics(report)` - Stent type, vessels treated, complications
- `assess_success_rate(metrics)` - Procedure success classification

### 6. **AlertService** (`services/alert_service.py`)
**Purpose**: Anomaly detection and alert generation

**Triggers**:
- Heart rate > 120 bpm or < 40 bpm
- BP > 160/100 mmHg
- SpO2 < 90%
- Temperature > 38.5°C or < 35°C
- Abnormal ECG findings
- Multiple high-risk predictions

**Actions**:
- In-app notifications
- Email alerts (configurable)
- SMS alerts (SMS gateway)
- Emergency contact notification

### 7. **LLMService** (`services/llm_service.py`)
**Purpose**: Large Language Model inference via Featherless AI

**Functions**:
- `generate_response(prompt, context)` - LLM text generation
- `summarize_health_data(data)` - Clinical summary generation
- `generate_recommendations(risk_profile)` - Health advice

**Model**: Meta-Llama-3-8B-Instruct (OpenAI-compatible API)

### 8. **VoiceService** (`services/voice_service.py`)
**Purpose**: Text-to-speech synthesis

**Providers**: ElevenLabs, Azure Speech Services

**Features**:
- Voice customization (gender, accent, speed)
- Audio streaming
- SSML support (for emphasis)

### 9. **ContextEngine** (`services/context_engine.py`)
**Purpose**: Conversation state management and intent detection

**Functions**:
- `detect_intent(message)` - Intent classification (greeting, predict, alert, etc.)
- `detect_emotional_state(message)` - Sentiment analysis (anxious, calm, urgent)
- `get_or_create_session(user_id)` - Retrieve/create conversation session

**Intent Classes**:
- `greeting` - Casual interactions
- `predict` - Prediction requests
- `monitor` - Vital sign queries
- `ecg` - ECG-related questions
- `angioplasty` - Procedure-related
- `heart_sound` - Audio analysis questions
- `history` - Historical data requests
- `alert` - Alert-related inquiries
- `medication` - Medicine/dosage questions
- `emergency` - Urgent medical situations
- `help` - General help

### 10. **DeepAgent** (`services/deep_agent.py`)
**Purpose**: Central orchestrator that coordinates all services

**Core Logic**:
```
1. Receive user message
2. Detect intent using ContextEngine
3. Detect emotional state (anxious, calm, urgent)
4. Route to appropriate service handler
5. Fetch relevant data from services/database
6. Generate contextual response via LLM + Jarvis personality
7. Add response to conversation history
8. Return formatted response (text + optional audio)
```

**Handlers**:
- `_handle_greeting()` - Friendly salutation
- `_handle_prediction()` - Risk prediction
- `_handle_monitoring()` - Vital signs check
- `_handle_ecg_chat()` - ECG-related queries
- `_handle_emergency()` - Emergency protocol
- `_handle_general()` - Fallback for other queries

### 11. **JarvisPersonality** (`services/jarvis_personality.py`)
**Purpose**: JARVIS AI personality and response styling

**Characteristics**:
- Professional yet friendly tone
- Context-aware communication style
- Empathetic to health concerns
- Evidence-based health advice
- Proactive health monitoring suggestions

**Response Formatting**:
- Greetings personalized with user name
- Medical findings explained in layman's terms
- Risk levels color-coded (Green/Yellow/Red)
- Actionable recommendations prioritized

### 12. **DataSourceIntegration** (`services/data_sources/`)
**Purpose**: Multi-source health data aggregation

**Connectors**:
- **GoogleFit**: Sync steps, heart rate, sleep, calories
- **Fitbit**: Access wearable vital signs and activity
- **Firebolt**: Enterprise health data warehouse queries
- **ManualEntry**: User-entered health metrics
- **DataFusion**: Normalize and merge data from all sources

**Data Fusion Logic**:
- Time-based alignment
- Conflict resolution (multiple sources reporting same metric)
- Data quality scoring
- Outlier detection and handling

---

## Working Flow

### 1. **User Registration & Login Flow**
```
User → POST /api/v1/auth/signup
     → Password hashed with bcrypt
     → User stored in DB
     → Welcome email sent
     
User → POST /api/v1/auth/login
     → Credentials verified
     → JWT token generated
     → Token returned to client
```

### 2. **Heart Attack Prediction Flow**
```
User → POST /api/v1/predict/heart-attack
     ↓
API validates input schema
     ↓
PredictionService.predict_heart_risk()
     ↓
Load ML model → Extract features → scikit-learn inference
     ↓
Generate risk score (0-100%) and classification
     ↓
AlertService checks if risk > threshold → Generate alert if needed
     ↓
Store prediction in DB
     ↓
Return response with risk_score, risk_level, recommendations
```

### 3. **ECG Image Analysis Flow**
```
User → POST /api/v1/analyze/ecg (multipart/form-data)
     ↓
Save image to /uploads/ecg_*.jpg
     ↓
ECGService.analyze_ecg_image()
     ├─ Image preprocessing (resize, normalize)
     ├─ Feature extraction (wave detection)
     ├─ Pattern recognition
     └─ Classification (Normal/Abnormal)
     ↓
Store analysis in DB with image reference
     ↓
AlertService checks findings → Alert if abnormal
     ↓
Return analysis with findings, confidence, recommendations
```

### 4. **Real-Time Monitoring Flow (WebSocket)**
```
Client → WebSocket connection to /api/v1/monitor/live/{userId}
     ↓
MonitoringService queries latest vitals
     ↓
Data sent to client every 5 seconds
     ↓
Client displays real-time dashboard
     ↓
AlertService monitors for anomalies
     ↓
If anomaly detected → Instant alert notification
```

### 5. **DeepAgent Conversation Flow**
```
User → WebSocket connection to /api/v1/agent/chat
     ↓
JSON payload: {"message": "...", "user_id": 1, "user_name": "John"}
     ↓
DeepAgent.process_message()
     ├─ ContextEngine.detect_intent() → "predict" / "monitor" / "help" / etc.
     ├─ ContextEngine.detect_emotional_state() → "anxious" / "calm" / etc.
     ├─ Create/retrieve conversation session
     ├─ Add user message to conversation history
     └─ Route to appropriate handler
     ↓
Handler executes (e.g., if intent="predict"):
     ├─ Query PredictionService for latest risk
     ├─ Fetch user health history from DB
     ├─ Format data context
     └─ Pass to LLMService
     ↓
LLMService generates response using Featherless AI:
     ├─ Build prompt with context
     ├─ Call API with Llama-3-8B-Instruct
     └─ Receive text response
     ↓
JarvisPersonality applies formatting and tone
     ↓
VoiceService converts text to speech (optional)
     ↓
Response sent back via WebSocket:
     ├─ response: "Your heart health looks great! HR 72 bpm..."
     ├─ audio: "base64-encoded-audio"
     └─ metadata: {"intent": "predict", "confidence": 0.95}
```

### 6. **Data Source Sync Flow**
```
User → GET /api/v1/data/sync/{userId}
     ↓
DataFusion loops through connected sources:
     ├─ GoogleFitConnector.fetch_vitals()
     ├─ FitbitConnector.fetch_vitals()
     ├─ FireboltConnector.query_records()
     └─ ManualEntryService.fetch_recent()
     ↓
Normalize data (units, timestamps)
     ↓
Merge and conflict resolution
     ↓
Store fused data in DB
     ↓
AlertService analyzes merged data
     ↓
Return consolidated health metrics
```

---

## Implementation Details

### Authentication System
- **Method**: JWT (JSON Web Tokens)
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Token Expiry**: 24 hours (configurable)
- **Refresh**: Refresh token endpoint available
- **Password Hashing**: bcrypt with salt rounds = 12

### Database Design
- **Type**: SQLite (development), can scale to PostgreSQL
- **ORM**: SQLAlchemy 2.0+ with async support
- **Tables**:
  - `users` - User accounts with roles
  - `health_records` - Vital signs history
  - `predictions` - ML prediction results
  - `ecg_analyses` - ECG image analysis records
  - `heart_sounds` - Audio analysis results
  - `alerts` - Generated alerts and notifications
  - `conversations` - Chat history with DeepAgent
  - `data_sources` - Connected data source credentials

### ML Model
- **Type**: Random Forest Classifier
- **Training Data**: UCI Heart Disease Dataset (303 samples)
- **Features**: 13 clinical parameters
- **Output**: Binary classification + probability scores
- **Framework**: scikit-learn with joblib serialization
- **Performance**: ~85% accuracy on validation set

### Error Handling
- **Validation**: Pydantic schema validation for all inputs
- **HTTP Exceptions**: Standardized error responses with status codes
- **Logging**: Structured logging to console and files
- **Rate Limiting**: Optional rate limiting per endpoint (configurable)

### Scalability Considerations
- **Async/Await**: All endpoints use FastAPI async support
- **Connection Pooling**: SQLAlchemy session management
- **Caching**: In-memory caching for frequently accessed data
- **Microservices-Ready**: Services can be extracted to separate containers
- **Database**: Easy migration from SQLite → PostgreSQL

---

## Configuration

### Environment Variables
See `.env` file template above for all available configurations.

### Logging
Configure in `config.py`:
```python
LOGGING_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Alert Thresholds
Configurable in `services/alert_service.py`:
```python
ALERTS = {
    "HIGH_HEART_RATE": 120,
    "LOW_HEART_RATE": 40,
    "HIGH_BP": (160, 100),
    "LOW_SPO2": 90,
    "HIGH_TEMP": 38.5,
    "LOW_TEMP": 35.0,
}
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Test LLM Service
```bash
pytest tests/test_llm.py -v
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Database Lock Error** | Remove `heart_health.db`, restart application |
| **ML Model Not Found** | Ensure `models/ml/heart_attack_model.pkl` exists or retrain: `python train/train_model.py` |
| **LLM API Errors** | Check `FEATHERLESS_API_KEY` in `.env` |
| **Voice Service Issues** | Verify `ELEVENLABS_API_KEY` configuration |
| **Port Already in Use** | Change `PORT` in `.env` or kill process on port 8000 |
| **Import Errors** | Ensure virtual environment is activated: `source venv/bin/activate` |

---

## Future Enhancements

- [ ] Mobile app integration (iOS/Android)
- [ ] Advanced waveform analysis (12-lead ECG)
- [ ] Integration with medical imaging (CT, MRI)
- [ ] Federated learning for privacy-preserving ML
- [ ] Blockchain-based health records
- [ ] Advanced voice recognition for symptom description
- [ ] Personalized medicine recommendations via genomics
- [ ] Real-world external healthcare provider EHR integration
- [ ] Advanced predictive analytics (LSTM, Transformer models)
- [ ] Multi-language support for global deployment

---

## License

[Specify your license here]

## Contributors

- Sujal Nivruti Pagere

## Support

For issues, questions, or contributions, please [contact or create an issue](link-to-issue-tracker).

---

**Last Updated**: April 5, 2026
**Version**: 2.0.0
