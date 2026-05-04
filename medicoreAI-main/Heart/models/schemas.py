"""
Heart Health Module - Pydantic Schemas
Request/response models with validation for all API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class DataSourceType(str, Enum):
    FIREBOLT = "firebolt"
    GOOGLE_FIT = "google_fit"
    FITBIT = "fitbit"
    MANUAL = "manual"
    MI_DIGITAL = "mi_digital"


class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


# ── Auth ───────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = None
    role: UserRole = UserRole.PATIENT


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Heart Attack Prediction ────────────────────────────

class HeartPredictionInput(BaseModel):
    """Input for heart attack risk prediction."""
    age: int = Field(..., ge=1, le=150, description="Patient age")
    sex: int = Field(..., ge=0, le=1, description="0=Female, 1=Male")
    cp: int = Field(..., ge=0, le=3, description="Chest pain type (0-3)")
    trestbps: float = Field(..., ge=50, le=300, description="Resting blood pressure")
    chol: float = Field(..., ge=50, le=600, description="Serum cholesterol mg/dl")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results (0-2)")
    thalach: float = Field(..., ge=50, le=250, description="Max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina")
    oldpeak: float = Field(..., ge=0, le=10, description="ST depression")
    slope: int = Field(..., ge=0, le=2, description="Slope of peak exercise ST")
    ca: int = Field(..., ge=0, le=4, description="Number of major vessels colored")
    thal: int = Field(..., ge=0, le=3, description="Thalassemia (0-3)")


class ContributingFactor(BaseModel):
    factor: str
    value: Any
    severity: str
    explanation: str


class HeartPredictionResponse(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    contributing_factors: List[ContributingFactor]
    summary: str
    tips: List[str]
    model_version: str = "v1.0"


# ── ECG Analysis ──────────────────────────────────────

class ECGAnalysisResponse(BaseModel):
    report_id: int
    summary: str
    detailed_explanation: str
    findings: List[str]
    recommendations: str
    risk_flags: List[str]
    timestamp: datetime


# ── Angioplasty Analysis ──────────────────────────────

class AngioplastyAnalysisResponse(BaseModel):
    report_id: int
    structured_summary: str
    stent_details: List[Dict[str, Any]]
    artery_locations: List[str]
    complications: Optional[str]
    explanation: str
    follow_up_instructions: str


# ── Heart Sound Analysis ──────────────────────────────

class HeartSoundResponse(BaseModel):
    recording_id: int
    classification: str
    confidence: float
    explanation: str
    features_detected: Dict[str, Any]


# ── Monitoring ────────────────────────────────────────

class VitalsData(BaseModel):
    heart_rate: Optional[float] = None
    hrv: Optional[float] = None
    spo2: Optional[float] = None
    steps: Optional[int] = None
    sleep_stage: Optional[str] = None
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    source: str = "manual"
    timestamp: Optional[datetime] = None


class AlertConfigCreate(BaseModel):
    metric: str = Field(..., description="heart_rate, spo2, hrv, blood_pressure")
    threshold_value: float
    direction: str = Field("above", description="above or below")
    enabled: bool = True
    notify_email: bool = False
    notify_push: bool = True


class AlertConfigResponse(BaseModel):
    id: int
    metric: str
    threshold_value: float
    direction: str
    enabled: bool

    class Config:
        from_attributes = True


class TrendData(BaseModel):
    dates: List[str]
    values: List[float]
    metric: str
    period: str
    average: float
    trend_direction: str  # improving, declining, stable


# ── Data Sources ──────────────────────────────────────

class DataSourceRegister(BaseModel):
    source_type: DataSourceType
    config: Dict[str, Any] = {}
    priority: int = Field(1, ge=1, le=10)


class DataSourceResponse(BaseModel):
    id: int
    source_type: str
    status: str
    last_sync: Optional[datetime]
    priority: int

    class Config:
        from_attributes = True


class ManualEntryInput(BaseModel):
    heart_rate: Optional[float] = None
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    spo2: Optional[float] = None
    weight_kg: Optional[float] = None
    symptoms: Optional[List[str]] = None
    medications_taken: Optional[List[str]] = None
    exercise_minutes: Optional[int] = None
    notes: Optional[str] = None


# ── DeepAgent / JARVIS ────────────────────────────────

class AgentCommand(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    response: str
    intent_detected: str
    data: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    emotional_tone: str = "calm"


class ConversationContextResponse(BaseModel):
    session_id: str
    turn_count: int
    recent_topics: List[str]
    pending_questions: List[str]
    emotional_state: str
    last_interaction: Optional[datetime]


# ── Health Summary ────────────────────────────────────

class HealthSummaryResponse(BaseModel):
    date: datetime
    metrics: Dict[str, Any]
    anomalies: List[str]
    insights: List[str]
    data_sources_used: List[str]
    jarvis_briefing: str
