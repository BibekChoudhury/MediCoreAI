# 🚀 MediCore AI — Quick Start Guide

## Prerequisites

| Tool         | Version    | Check Command         |
|--------------|------------|-----------------------|
| Python       | ≥ 3.11     | `python3 --version`   |
| Node.js      | ≥ 18       | `node --version`      |
| npm          | ≥ 9        | `npm --version`       |
| pip          | latest     | `pip --version`       |

---

## 1. Clone & Navigate

```bash
git clone <repo-url> medicoreAI-main
cd medicoreAI-main
```

---

## 2. Environment Variables

### Root `.env` (Required)

Create `.env` in the project root:

```env
# Groq API Key — Required for AI Consultation, Prescription Analyzer, Health Report Analyzer
# Get yours at: https://console.groq.com/keys
GROQ_API_KEY=your-groq-api-key-here

# JWT Authentication
JWT_SECRET_KEY=replace-this-secret-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REMEMBER_ME_EXPIRE_DAYS=30
```

### Heart Module `.env` (Required for Heart Health features)

Create `Heart/.env`:

```env
# Database
DATABASE_URL=sqlite:///heart_health.db

# JWT
SECRET_KEY=your-secret-key-here

# OpenRouter API — Powers the Cardia AI chatbot
# Get yours at: https://openrouter.ai/keys
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-opus-4.7

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

> **Note:** `ELEVENLABS_API_KEY`, `GOOGLE_FIT_CLIENT_ID/SECRET`, and `FITBIT_*` keys are optional. The app works without them using browser TTS and Health Connect sync.

---

## 3. Install Dependencies

### Backend (Python)

```bash
# Create virtual environment (one-time)
python3 -m venv Heart/.venv

# Activate it
source Heart/.venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Frontend (Node.js)

```bash
cd MEDI_CORE_ASSIST/frontend
npm install
cd ../..
```

---

## 4. Start the Application

You need **two terminals** running simultaneously:

### Terminal 1 — Backend (FastAPI on port 8000)

```bash
cd backend
../Heart/.venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:main:Heart Health Module mounted at /heart
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2 — Frontend (Vite on port 3000)

```bash
cd MEDI_CORE_ASSIST/frontend
npm run dev
```

Expected output:
```
VITE v6.4.1  ready in 147 ms
➜  Local:   http://localhost:3000/
```

---

## 5. Open the Application

Open your browser and go to:

```
http://localhost:3000
```

- **Sign up** with a new account (first-time use)
- **Log in** to access the dashboard

---

## 6. Quick Verification

After both servers are running, verify everything works:

```bash
# Check backend health
curl http://localhost:8000/health

# Check Heart module is mounted
curl http://localhost:8000/heart/api/v1/data/sync/all -X POST

# Check Cardia AI chatbot
curl -X POST http://localhost:8000/heart/api/v1/agent/command \
  -H "Content-Type: application/json" \
  -d '{"message":"hello","user_id":1}'
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY is not set` | Add your Groq API key to root `.env` |
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill -9` |
| Port 3000 already in use | `lsof -ti:3000 \| xargs kill -9` |
| `ModuleNotFoundError` | Re-activate venv: `source Heart/.venv/bin/activate` |
| Heart module not mounting | Check `Heart/` directory exists at project root |
| Cardia returns template responses | Verify `OPENROUTER_API_KEY` in `Heart/.env` is valid |
| scikit-learn version warning | Safe to ignore — model still works |

---

## Stopping the Application

Press `Ctrl+C` in both terminal windows, or:

```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```
