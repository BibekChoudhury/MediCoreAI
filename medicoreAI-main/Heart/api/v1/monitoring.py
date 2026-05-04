"""
Heart Health Module - Monitoring Routes
Real-time monitoring, WebSocket, trend analysis, and alert configuration
"""
import json
import asyncio
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from models.database import get_db, SessionLocal
from models.schemas import VitalsData, AlertConfigCreate, AlertConfigResponse
from services.monitoring_service import store_vitals, get_latest_vitals, get_history, generate_health_summary
from services.alert_service import create_alert_config, get_alert_configs, check_alerts
from services.watch_service import FireboltSimulator
from api.deps import get_current_user

router = APIRouter(prefix="/monitor", tags=["Monitoring"])


# ── WebSocket connections ─────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: dict = {}  # user_id -> WebSocket

    async def connect(self, ws: WebSocket, user_id: int):
        await ws.accept()
        self.active[user_id] = ws

    def disconnect(self, user_id: int):
        self.active.pop(user_id, None)

    async def send(self, user_id: int, data: dict):
        ws = self.active.get(user_id)
        if ws:
            await ws.send_json(data)


manager = ConnectionManager()


@router.websocket("/live/{user_id}")
async def ws_live_monitoring(ws: WebSocket, user_id: int):
    """WebSocket for real-time vitals streaming - ONLY uses Health Connect data from Android app."""
    await manager.connect(ws, user_id)

    try:
        while True:
            db = SessionLocal()
            try:
                from models.db_models import WatchData
                from sqlalchemy import desc
                
                # ⚡ ONLY get health_connect data - no fallback, no simulation
                # Try both numeric and string user_id formats (Android app sends "cardia_user_1")
                latest_hc = db.query(WatchData).filter(
                    WatchData.source == 'health_connect'
                ).order_by(desc(WatchData.timestamp)).first()
                
                if latest_hc:
                    # Stream ONLY health_connect data
                    reading = {
                        "heart_rate": latest_hc.heart_rate,
                        "spo2": latest_hc.spo2,
                        "hrv": latest_hc.hrv,
                        "steps": latest_hc.steps,
                        "sleep_stage": latest_hc.sleep_stage or "awake",
                        "source": "health_connect",
                        "timestamp": latest_hc.timestamp.isoformat() if latest_hc.timestamp is not None else None,
                    }
                    print(f"📱 HEALTH_CONNECT ONLY: HR={reading['heart_rate']} SpO2={reading['spo2']} HRV={reading['hrv']} Steps={reading['steps']}")
                    
                    # Check alerts
                    alerts = check_alerts(db, user_id, reading)
                    if alerts:
                        reading["alerts"] = alerts
                else:
                    # No health_connect data available - send null/empty
                    reading = {
                        "heart_rate": None,
                        "spo2": None,
                        "hrv": None,
                        "steps": None,
                        "sleep_stage": "unknown",
                        "source": "health_connect",
                        "timestamp": None,
                        "message": "⏳ Waiting for Health Connect data from Android app..."
                    }
                    print(f"⏳ No health_connect data yet - waiting for Android app sync")
            finally:
                db.close()

            await ws.send_json(reading)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(user_id)


# ── REST Endpoints ────────────────────────────────────

@router.post("/vitals")
def api_submit_vitals(data: VitalsData, db: Session = Depends(get_db),
                      user=Depends(get_current_user)):
    """Submit vitals data (manual or from sync)."""
    user_id = user.id if user else 1
    entry = store_vitals(db, user_id, data.model_dump())
    return {"status": "stored", "id": entry.id}


@router.get("/latest/{user_id}")
def api_latest_vitals(user_id: int, db: Session = Depends(get_db)):
    """Get latest vitals for a user."""
    vitals = get_latest_vitals(db, user_id)
    if not vitals:
        return {"message": "No vitals data found", "data": None}
    return {"data": vitals}


@router.get("/trends/{user_id}")
def api_trends(user_id: int,
               metric: str = Query("heart_rate", description="Metric to trend"),
               period: str = Query("week", description="day, week, month, year"),
               db: Session = Depends(get_db)):
    """Get trend data for a specific metric."""
    return get_history(db, user_id, metric, period)


@router.get("/history/{user_id}")
def api_history(user_id: int,
                limit: int = Query(50, description="Number of records"),
                db: Session = Depends(get_db)):
    """Get historical vitals records for a user."""
    from models.db_models import WatchData
    from sqlalchemy import desc
    
    records = db.query(WatchData).filter(
        WatchData.user_id == user_id
    ).order_by(desc(WatchData.timestamp)).limit(limit).all()
    
    if not records:
        return {"message": "No vitals data found", "latest": None, "history": []}
    
    history = [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp is not None else None,
            "heart_rate": r.heart_rate,
            "spo2": r.spo2,
            "steps": r.steps,
            "sys_bp": r.blood_pressure_systolic,
            "dia_bp": r.blood_pressure_diastolic,
            "calories": r.calories_burned,
            "sleep_stage": r.sleep_stage,
            "source": r.source,
        }
        for r in records
    ]
    
    latest = history[0] if history else None
    return {
        "latest": latest,
        "history": history,
        "total_records": len(history)
    }


@router.get("/summary/{user_id}")
def api_health_summary(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive health summary."""
    from services.jarvis_personality import jarvis
    summary = generate_health_summary(db, user_id)
    if not summary:
        return {"message": "Not enough data for summary"}

    summary["jarvis_briefing"] = jarvis.health_briefing("User", summary)
    return summary


# ── Alert Configuration ──────────────────────────────

@router.post("/alerts")
def api_create_alert(data: AlertConfigCreate, db: Session = Depends(get_db),
                     user=Depends(get_current_user)):
    """Create or update alert threshold."""
    user_id = user.id if user else 1
    alert = create_alert_config(db, user_id, data.model_dump())
    return AlertConfigResponse.model_validate(alert)


@router.get("/alerts/{user_id}")
def api_get_alerts(user_id: int, db: Session = Depends(get_db)):
    """Get all alert configs for a user."""
    configs = get_alert_configs(db, user_id)
    return [AlertConfigResponse.model_validate(c) for c in configs]
