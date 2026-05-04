"""
Heart Health Module - Monitoring Service
Real-time health monitoring, vitals tracking, and trend analysis
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models.db_models import WatchData, HealthSummary


def store_vitals(db: Session, user_id: int, data: dict) -> WatchData:
    """Store incoming vitals data."""
    entry = WatchData(
        user_id=user_id,
        source=data.get("source", "manual"),
        heart_rate=data.get("heart_rate"),
        hrv=data.get("hrv"),
        spo2=data.get("spo2"),
        steps=data.get("steps"),
        sleep_stage=data.get("sleep_stage"),
        blood_pressure_systolic=data.get("blood_pressure_systolic"),
        blood_pressure_diastolic=data.get("blood_pressure_diastolic"),
        calories_burned=data.get("calories_burned"),
        activity_minutes=data.get("activity_minutes"),
        raw_data=data,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_latest_vitals(db: Session, user_id: int) -> Optional[Dict]:
    """Get the most recent vitals for a user - ONLY from health_connect source."""
    # ✅ HEALTH_CONNECT_ONLY: Only get data from Android Health Connect
    entry = db.query(WatchData).filter(
        WatchData.source == 'health_connect'
    ).order_by(desc(WatchData.timestamp)).first()

    if not entry:
        return None

    return {
        "heart_rate": entry.heart_rate,
        "hrv": entry.hrv,
        "spo2": entry.spo2,
        "steps": entry.steps,
        "sleep_stage": entry.sleep_stage,
        "blood_pressure_systolic": entry.blood_pressure_systolic,
        "blood_pressure_diastolic": entry.blood_pressure_diastolic,
        "source": entry.source,
        "timestamp": entry.timestamp.isoformat() if entry.timestamp is not None else None,
    }


def get_history(db: Session, user_id: int, metric: str,
                period: str = "week") -> Dict:
    """Get historical trend data for a specific metric."""
    now = datetime.utcnow()
    period_map = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365),
    }
    delta = period_map.get(period, timedelta(weeks=1))
    start = now - delta

    entries = db.query(WatchData).filter(
        WatchData.user_id == user_id,
        WatchData.timestamp >= start
    ).order_by(WatchData.timestamp).all()

    dates = []
    values = []
    for e in entries:
        val = getattr(e, metric, None)
        if val is not None:
            dates.append(e.timestamp.strftime("%Y-%m-%d %H:%M"))
            values.append(float(val))

    avg = sum(values) / len(values) if values else 0

    # Determine trend direction
    trend = "stable"
    if len(values) >= 4:
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        diff_pct = ((second_half - first_half) / first_half * 100) if first_half else 0
        if diff_pct > 5:
            trend = "increasing"
        elif diff_pct < -5:
            trend = "decreasing"

    return {
        "dates": dates,
        "values": values,
        "metric": metric,
        "period": period,
        "average": round(avg, 2),
        "trend_direction": trend,
        "data_points": len(values),
    }


def generate_health_summary(db: Session, user_id: int) -> Optional[Dict]:
    """Generate a comprehensive health summary from recent data - ONLY from health_connect."""
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)

    # ✅ HEALTH_CONNECT_ONLY: Only use data from Android Health Connect
    entries = db.query(WatchData).filter(
        WatchData.source == 'health_connect',
        WatchData.timestamp >= day_ago
    ).all()

    if not entries:
        return None

    heart_rates = [e.heart_rate for e in entries if e.heart_rate is not None]
    hrvs = [e.hrv for e in entries if e.hrv is not None]
    spo2s = [e.spo2 for e in entries if e.spo2 is not None]
    steps_list = [e.steps for e in entries if e.steps is not None]

    avg_hr = sum(heart_rates) / len(heart_rates) if heart_rates else None
    avg_hrv = sum(hrvs) / len(hrvs) if hrvs else None
    avg_spo2 = sum(spo2s) / len(spo2s) if spo2s else None
    total_steps = max(steps_list) if steps_list else 0

    # Detect anomalies
    anomalies = []
    if avg_hr is not None and avg_hr > 100:  # type: ignore
        anomalies.append(f"Elevated average heart rate: {round(avg_hr)} bpm")  # type: ignore
    if avg_hr is not None and avg_hr < 50:  # type: ignore
        anomalies.append(f"Low average heart rate: {round(avg_hr)} bpm")  # type: ignore
    if avg_spo2 is not None and avg_spo2 < 94:  # type: ignore
        anomalies.append(f"Low blood oxygen: {round(avg_spo2, 1)}%")  # type: ignore
    if avg_hrv is not None and avg_hrv < 20:  # type: ignore
        anomalies.append(f"Reduced HRV: {round(avg_hrv)}ms — may indicate stress")  # type: ignore

    # Generate insights
    insights = []
    if total_steps > 8000:  # type: ignore
        insights.append("Great activity level today! You've exceeded 8,000 steps.")
    elif total_steps > 4000:  # type: ignore
        insights.append(f"You've taken {total_steps} steps. Try to reach 8,000 for optimal heart health.")
    if avg_hrv is not None and avg_hrv > 40:  # type: ignore
        insights.append("Your HRV is healthy, indicating good autonomic nervous system function.")

    # Sleep quality assessment
    sleep_entries = [e.sleep_stage for e in entries if e.sleep_stage is not None]  # type: ignore
    sleep_quality = "unknown"
    if sleep_entries:
        deep_count = sum(1 for stage in sleep_entries if stage == "deep") + sum(1 for stage in sleep_entries if stage == "rem")  # type: ignore
        if deep_count > len(sleep_entries) * 0.3:
            sleep_quality = "excellent"
        elif deep_count > len(sleep_entries) * 0.2:
            sleep_quality = "good"
        else:
            sleep_quality = "fair"

    sources = list(set(e.source for e in entries if e.source is not None))  # type: ignore

    return {
        "avg_heart_rate": round(avg_hr, 1) if avg_hr is not None else None,  # type: ignore
        "avg_hrv": round(avg_hrv, 1) if avg_hrv is not None else None,  # type: ignore
        "avg_spo2": round(avg_spo2, 1) if avg_spo2 is not None else None,  # type: ignore
        "total_steps": total_steps,
        "sleep_quality": sleep_quality,
        "anomalies": anomalies,
        "insights": insights,
        "data_sources_used": sources,
        "data_points": len(entries),
    }
