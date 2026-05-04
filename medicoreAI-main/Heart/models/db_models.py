"""
Heart Health Module - SQLAlchemy ORM Models
All database table definitions
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, JSON, ForeignKey
)
from sqlalchemy.sql import func
from models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    age = Column(Integer)
    gender = Column(String(20))
    role = Column(String(20), default="patient")  # patient, doctor, admin
    medical_history = Column(JSON, default=dict)
    risk_factors = Column(JSON, default=dict)
    preferences = Column(JSON, default=dict)  # JARVIS prefs: explanation_depth, alert_sensitivity
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WatchData(Base):
    __tablename__ = "watch_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    source = Column(String(50), default="firebolt")  # firebolt, google_fit, fitbit, manual
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    heart_rate = Column(Float)
    hrv = Column(Float)
    spo2 = Column(Float)
    steps = Column(Integer)
    sleep_stage = Column(String(30))  # awake, light, deep, rem
    blood_pressure_systolic = Column(Float)
    blood_pressure_diastolic = Column(Float)
    calories_burned = Column(Float)
    activity_minutes = Column(Integer)
    raw_data = Column(JSON, default=dict)


class ECGReport(Base):
    __tablename__ = "ecg_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    file_url = Column(String(500))
    file_type = Column(String(20))  # image, pdf, digital
    raw_text = Column(Text)
    summary = Column(Text)
    detailed_explanation = Column(Text)
    findings = Column(JSON, default=list)
    recommendations = Column(Text)
    risk_flags = Column(JSON, default=list)


class AngioplastyReport(Base):
    __tablename__ = "angioplasty_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    date = Column(DateTime, server_default=func.now())
    report_text = Column(Text)
    extracted_findings = Column(JSON, default=dict)
    stent_details = Column(JSON, default=list)
    artery_locations = Column(JSON, default=list)
    complications = Column(Text)
    explanation = Column(Text)
    follow_up_instructions = Column(Text)


class HeartSoundRecording(Base):
    __tablename__ = "heart_sound_recordings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    audio_url = Column(String(500))
    duration_seconds = Column(Float)
    classification = Column(String(50))
    confidence = Column(Float)
    explanation = Column(Text)
    features = Column(JSON, default=dict)


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    contributing_factors = Column(JSON, default=list)
    model_version = Column(String(50), default="v1.0")
    input_data = Column(JSON, default=dict)


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    metric = Column(String(50), nullable=False)  # heart_rate, spo2, hrv, blood_pressure
    threshold_value = Column(Float, nullable=False)
    direction = Column(String(10), default="above")  # above, below
    enabled = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=False)
    notify_push = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    source_type = Column(String(50), nullable=False)  # firebolt, google_fit, fitbit, manual, mi_digital
    status = Column(String(20), default="active")  # active, inactive, error
    last_sync = Column(DateTime)
    config = Column(JSON, default=dict)
    priority = Column(Integer, default=1)  # Higher priority sources override
    created_at = Column(DateTime, server_default=func.now())


class ConversationContext(Base):
    __tablename__ = "conversation_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String(100), index=True)
    turn_count = Column(Integer, default=0)
    recent_topics = Column(JSON, default=list)
    pending_questions = Column(JSON, default=list)
    emotional_state = Column(String(30), default="calm")
    conversation_history = Column(JSON, default=list)
    last_interaction = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(200))
    details = Column(JSON, default=dict)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, server_default=func.now())


class HealthSummary(Base):
    __tablename__ = "health_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    date = Column(DateTime, server_default=func.now(), index=True)
    avg_heart_rate = Column(Float)
    avg_hrv = Column(Float)
    avg_spo2 = Column(Float)
    total_steps = Column(Integer)
    sleep_quality = Column(String(20))
    activity_minutes = Column(Integer)
    anomalies = Column(JSON, default=list)
    insights = Column(JSON, default=list)
    data_sources_used = Column(JSON, default=list)
