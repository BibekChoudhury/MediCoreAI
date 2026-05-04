"""
Heart Health Module - Data Sources Routes
Multi-source registration, sync, manual entry, and OAuth endpoints
"""
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import DataSourceRegister, DataSourceResponse, ManualEntryInput
from services.data_sources.data_fusion import data_fusion
from services.monitoring_service import store_vitals
from api.deps import get_current_user
import config

router = APIRouter(prefix="/data", tags=["Data Sources"])


@router.post("/source/register")
def api_register_source(data: DataSourceRegister,
                        db: Session = Depends(get_db),
                        user=Depends(get_current_user)):
    """Register a new data source (Google Fit, Fitbit, Firebolt, manual)."""
    user_id = user.id if user else 1
    result = data_fusion.register_source(
        user_id, data.source_type.value, data.config, data.priority
    )

    # Also save to DB
    from models.db_models import DataSource as DS
    ds = DS(
        user_id=user_id,
        source_type=data.source_type.value,
        status="active",
        config=data.config,
        priority=data.priority,
    )
    db.add(ds)
    db.commit()

    return result


@router.get("/sources/{user_id}")
def api_get_sources(user_id: int):
    """List all connected data sources for a user."""
    return data_fusion.get_sources(user_id)


@router.get("/google-fit/auth-url")
def api_google_fit_auth_url():
    """Get Google Fit OAuth2 authorization URL."""
    from services.data_sources.google_fit import GoogleFitConnector
    connector = GoogleFitConnector(user_id=1)
    auth_url = connector.get_oauth_url()
    return {"auth_url": auth_url}


@router.get("/callback/google-fit")
async def api_google_fit_callback(code: str = "", error: str = "",
                                   db: Session = Depends(get_db)):
    """Handle Google Fit OAuth2 callback."""
    if error:
        return HTMLResponse(content=f"""
        <html><body style="background:#020408;color:#ff3344;font-family:Orbitron,monospace;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
        <div><h2>❌ Connection Failed</h2><p>{error}</p><p>You can close this window.</p>
        <script>setTimeout(()=>window.close(),3000)</script></div></body></html>
        """)

    if code:
        try:
            from services.data_sources.google_fit import GoogleFitConnector
            from models.db_models import DataSource as DS
            
            connector = GoogleFitConnector(user_id=1)
            success = await connector.exchange_code(code)

            if success:
                # Save the tokens to the database for future use
                existing_source = db.query(DS).filter(
                    DS.user_id == 1,
                    DS.source_type == "google_fit"
                ).first()
                
                if existing_source:
                    # Update existing source with new tokens
                    existing_source.config = {
                        "access_token": connector.access_token,
                        "refresh_token": connector.refresh_token,
                        "token_type": "Bearer"
                    }
                    existing_source.status = "active"
                else:
                    # Create new source with tokens
                    new_source = DS(
                        user_id=1,
                        source_type="google_fit",
                        status="active",
                        config={
                            "access_token": connector.access_token,
                            "refresh_token": connector.refresh_token,
                            "token_type": "Bearer"
                        },
                        priority=1
                    )
                    db.add(new_source)
                
                db.commit()
                
                # Also register in data fusion
                data_fusion.register_source(1, "google_fit")

                return HTMLResponse(content="""
                <html><body style="background:#020408;color:#00ff88;font-family:Orbitron,monospace;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
                <div><h2>✅ Google Fit Connected!</h2><p>Your health data is now syncing 🎉</p><p>This window will close automatically...</p>
                <script>setTimeout(()=>window.close(),3000)</script></div></body></html>
                """)
        except Exception as e:
            return HTMLResponse(content=f"""
            <html><body style="background:#020408;color:#ff8800;font-family:Orbitron,monospace;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
            <div><h2>⚠️ Connection Issue</h2><p>{str(e)}</p><p>You can close this window.</p>
            <script>setTimeout(()=>window.close(),3000)</script></div></body></html>
            """)

    return HTMLResponse(content="""
    <html><body style="background:#020408;color:#4a6a8a;font-family:Orbitron,monospace;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
    <div><h2>No authorization code received</h2><p>Please try connecting again.</p>
    <script>setTimeout(()=>window.close(),3000)</script></div></body></html>
    """)


@router.post("/sync/google-fit")
async def api_sync_google_fit(db: Session = Depends(get_db),
                               user=Depends(get_current_user)):
    """DISABLED - Google Fit sync is disabled to prevent interference with Health Connect data."""
    return {
        "status": "disabled",
        "message": "🚫 Google Fit sync disabled. Only Health Connect data from Android app is used.",
        "latest": None
    }


@router.post("/sync/fitbit")
async def api_sync_fitbit(db: Session = Depends(get_db),
                           user=Depends(get_current_user)):
    """DISABLED - Fitbit sync is disabled to prevent interference with Health Connect data."""
    return {
        "status": "disabled",
        "message": "🚫 Fitbit sync disabled. Only Health Connect data from Android app is used.",
        "latest": None
    }


@router.post("/manual")
def api_manual_entry(data: ManualEntryInput,
                     db: Session = Depends(get_db),
                     user=Depends(get_current_user)):
    """Submit manual health data entry."""
    user_id = user.id if user else 1

    entry_data = data.model_dump()
    entry_data["source"] = "manual"

    # Store in main watch_data table
    vitals = {k: v for k, v in entry_data.items() if v is not None}
    entry = store_vitals(db, user_id, vitals)

    return {
        "status": "recorded",
        "entry_id": entry.id,
        "message": "Health data logged successfully",
    }


@router.post("/sync/all")
async def api_sync_all(db: Session = Depends(get_db),
                       user=Depends(get_current_user)):
    """
    DISABLED: No longer syncs all sources.
    
    This endpoint is now disabled to prevent Firebolt simulation data from interfering
    with real Health Connect data from your Android phone.
    
    Only Health Connect data from Android app is used.
    """
    return {
        "status": "disabled",
        "message": "🚫 Auto-sync disabled. Only Health Connect data from Android app is used.",
        "latest": None
    }


@router.post("/health/submit")
def api_health_submit(data: dict, db: Session = Depends(get_db)):
    """
    Receive real health data from Android companion app via Health Connect.
    
    Modern 2026 architecture:
    Android Health Connect → Companion App (Kotlin) 
        → POST http://laptop-ip:8000/api/v1/data/health/submit 
        → This endpoint → Database
    
    Supports both flat and summary structures:
    Flat: {"user_id": 1, "steps": 5421, "heart_rate": 72, "spo2": 97.2, "hrv": 45, "source": "health_connect"}
    Summary: {"user_id": 1, "source": "health_connect", "summary": {"steps": 5421, "heart_rate": 72, "spo2": 97.2, "hrv": 45}}
    
    See: ANDROID_HEALTH_CONNECT_2026.md for full setup guide
    """
    try:
        from models.db_models import WatchData
        
        user_id = data.get("user_id", 1)
        source = data.get("source", "health_connect")
        
        # Handle both flat and summary payload structures
        summary = data.get("summary", {})
        
        # Extract values (check summary first, then fall back to flat structure)
        steps = summary.get("steps") or data.get("steps")
        heart_rate = summary.get("heart_rate") or data.get("heart_rate")
        spo2 = summary.get("spo2") or data.get("spo2")
        hrv = summary.get("hrv") or data.get("hrv")
        sleep_stage = summary.get("sleep_stage") or data.get("sleep_stage", "awake")
        
        # Create watch data entry with real Android health data
        watch_data = WatchData(
            user_id=user_id,
            source=source,
            heart_rate=heart_rate,
            steps=steps,
            spo2=spo2,
            hrv=hrv,
            sleep_stage=sleep_stage,
            raw_data=json.dumps(data),
        )
        
        db.add(watch_data)
        db.commit()
        db.refresh(watch_data)
        
        # Store vitals for alerts/monitoring
        store_vitals(db, user_id, {
            "heart_rate": heart_rate,
            "steps": steps,
            "spo2": spo2,
            "hrv": hrv,
            "source": source,
        })
        
        print(f"✅ Android health data received: {steps} steps, {heart_rate} bpm, {spo2}% SpO2, {hrv} HRV from {source}")
        
        return {
            "status": "success",
            "message": "Health data stored successfully",
            "record_id": watch_data.id,
            "source": source,
            "data_received": {
                "steps": steps,
                "heart_rate": heart_rate,
                "spo2": spo2,
                "hrv": hrv,
            }
        }
        
    except Exception as e:
        print(f"❌ Error storing Android health data: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}, 400
