"""
Heart Health Module - Alert Service
Threshold-based alerting with escalation and notification dispatch
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.db_models import AlertConfig, WatchData


def create_alert_config(db: Session, user_id: int, data: dict) -> AlertConfig:
    """Create a new alert configuration."""
    alert = AlertConfig(
        user_id=user_id,
        metric=data["metric"],
        threshold_value=data["threshold_value"],
        direction=data.get("direction", "above"),
        enabled=data.get("enabled", True),
        notify_email=data.get("notify_email", False),
        notify_push=data.get("notify_push", True),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alert_configs(db: Session, user_id: int) -> List[AlertConfig]:
    """Get all alert configurations for a user."""
    return db.query(AlertConfig).filter(
        AlertConfig.user_id == user_id,
        AlertConfig.enabled == True
    ).all()


def check_alerts(db: Session, user_id: int, vitals: dict) -> List[Dict]:
    """Check current vitals against configured alert thresholds."""
    configs = get_alert_configs(db, user_id)
    triggered_alerts = []

    for config in configs:
        value = vitals.get(config.metric)
        if value is None:
            continue

        triggered = False
        if config.direction == "above" and value > config.threshold_value:
            triggered = True
        elif config.direction == "below" and value < config.threshold_value:
            triggered = True

        if triggered:
            severity = _determine_severity(config.metric, value, config.threshold_value, config.direction)
            triggered_alerts.append({
                "metric": config.metric,
                "current_value": value,
                "threshold": config.threshold_value,
                "direction": config.direction,
                "severity": severity,
                "message": _format_alert_message(config.metric, value, config.threshold_value, config.direction),
                "timestamp": datetime.utcnow().isoformat()
            })

    return triggered_alerts


def _determine_severity(metric: str, value: float, threshold: float, direction: str) -> str:
    """Determine alert severity based on how far the value exceeds threshold."""
    if direction == "above":
        deviation = (value - threshold) / threshold * 100
    else:
        deviation = (threshold - value) / threshold * 100

    # Critical thresholds
    critical_conditions = {
        "heart_rate": (value > 180 or value < 40),
        "spo2": (value < 88),
        "blood_pressure_systolic": (value > 180 or value < 80),
    }

    if critical_conditions.get(metric, False):
        return "emergency"
    elif deviation > 30:
        return "critical"
    elif deviation > 15:
        return "warning"
    return "info"


def _format_alert_message(metric: str, value: float, threshold: float, direction: str) -> str:
    """Generate human-readable alert message."""
    metric_labels = {
        "heart_rate": ("Heart rate", "bpm"),
        "spo2": ("Blood oxygen (SpO2)", "%"),
        "hrv": ("Heart rate variability", "ms"),
        "blood_pressure_systolic": ("Systolic blood pressure", "mmHg"),
        "blood_pressure_diastolic": ("Diastolic blood pressure", "mmHg"),
    }
    label, unit = metric_labels.get(metric, (metric, ""))

    if direction == "above":
        return f"{label} is elevated at {round(value, 1)} {unit} (threshold: {threshold} {unit})"
    else:
        return f"{label} has dropped to {round(value, 1)} {unit} (threshold: {threshold} {unit})"
