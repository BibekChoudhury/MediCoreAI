"""
Heart Health Module v2 - Configuration
Environment-based configuration using Pydantic BaseSettings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'heart_health.db'}")

# JWT Auth
SECRET_KEY = os.getenv("SECRET_KEY", "heart-health-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Model paths
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", str(BASE_DIR / "models" / "ml" / "heart_attack_model.pkl"))

# External API keys (optional - uses simulated data when not set)
GOOGLE_FIT_CLIENT_ID = os.getenv("GOOGLE_FIT_CLIENT_ID", "")
GOOGLE_FIT_CLIENT_SECRET = os.getenv("GOOGLE_FIT_CLIENT_SECRET", "")
FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID", "")
FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET", "")

# Voice/TTS (optional)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")

# LLM Provider — OpenRouter (OpenAI-compatible)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", os.getenv("FEATHERLESS_API_KEY", ""))
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "MediCore-AI-HeartHealth")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Alert settings
ALERT_EMAIL_ENABLED = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Auto-sync settings
# 🚫 DISABLED: Only Health Connect data from Android app will be used
AUTO_SYNC_ENABLED = os.getenv("AUTO_SYNC_ENABLED", "false").lower() == "true"
AUTO_SYNC_INTERVAL_MINUTES = int(os.getenv("AUTO_SYNC_INTERVAL_MINUTES", "5"))

# Upload settings
UPLOAD_DIR = str(BASE_DIR / "uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
