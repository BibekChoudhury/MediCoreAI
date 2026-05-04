"""
Heart Health Module v2 – Main Application
FastAPI entry point with all routers, CORS, and static files
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import asyncio
import config
from models.database import init_db, SessionLocal
from models.db_models import User


# Background auto-sync task
sync_task = None

async def auto_sync_task():
    """Periodically sync data from all connected sources."""
    if not config.AUTO_SYNC_ENABLED:
        return
    
    while True:
        try:
            await asyncio.sleep(config.AUTO_SYNC_INTERVAL_MINUTES * 60)
            
            from services.data_sources.data_fusion import data_fusion
            from models.db_models import User as UserModel
            db = SessionLocal()
            
            try:
                # Get all users
                users = db.query(UserModel).all()
                
                for user in users:
                    try:
                        print(f"🔄 Auto-syncing data for user {user.id}...")
                        result = await data_fusion.sync_all(user.id)  # type: ignore
                        
                        # Store synced data
                        if result.get("latest"):
                            from services.monitoring_service import store_vitals
                            store_vitals(db, user.id, result["latest"])  # type: ignore
                        
                        print(f"✅ Auto-sync completed for user {user.id}")
                    except Exception as e:
                        print(f"❌ Auto-sync failed for user {user.id}: {e}")
            finally:
                db.close()
        except Exception as e:
            print(f"Auto-sync error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global sync_task
    
    # Startup: create database tables
    init_db()
    print("🫀 Heart Health Module v2 — Starting up...")
    print(f"📊 Dashboard: http://localhost:{config.PORT}/static/dashboard/index.html")
    print(f"📚 API Docs:  http://localhost:{config.PORT}/docs")
    
    # Start auto-sync task
    sync_task = None
    if config.AUTO_SYNC_ENABLED:
        print(f"🔄 Auto-sync enabled (every {config.AUTO_SYNC_INTERVAL_MINUTES} minutes)")
        sync_task = asyncio.create_task(auto_sync_task())
    
    yield
    
    # Shutdown
    if sync_task is not None:
        sync_task.cancel()
    print("Heart Health Module — Shutting down.")


app = FastAPI(
    title="Heart Health Module v2",
    description=(
        "Comprehensive heart health platform powered by DeepAgent with JARVIS-like "
        "conversational interface. Features: Heart attack prediction, ECG analysis, "
        "angioplasty report analysis, heart sound analysis, multi-source data integration, "
        "and real-time health monitoring."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API Routers ─────────────────────────────────

from api.v1.auth import router as auth_router
from api.v1.prediction import router as prediction_router
from api.v1.monitoring import router as monitoring_router
from api.v1.ecg_analysis import router as ecg_router
from api.v1.angiography_analysis import router as angioplasty_router
from api.v1.heart_sound import router as heart_sound_router
from api.v1.watch import router as watch_router
from api.v1.agent import router as agent_router
from api.v1.data_sources import router as data_sources_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(prediction_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(ecg_router, prefix="/api/v1")
app.include_router(angioplasty_router, prefix="/api/v1")
app.include_router(heart_sound_router, prefix="/api/v1")
app.include_router(watch_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(data_sources_router, prefix="/api/v1")

# ── Static Files (Dashboard) ─────────────────────────

static_dir = os.path.join(config.BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Uploads directory
uploads_dir = os.path.join(config.BASE_DIR, "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# ── Root ──────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {
        "module": "Heart Health Module v2",
        "version": "2.0.0",
        "powered_by": "DeepAgent + JARVIS",
        "endpoints": {
            "docs": "/docs",
            "dashboard": "/static/dashboard/index.html",
            "prediction": "/api/v1/predict/heart-attack",
            "monitoring": "/api/v1/monitor/live/{userId}",
            "ecg_analysis": "/api/v1/analyze/ecg",
            "angiography_analysis": "/api/v1/analyze/angiography",
            "heart_sound": "/api/v1/analyze/heart-sound",
            "agent_chat": "/api/v1/agent/chat (WebSocket)",
            "data_sources": "/api/v1/data/sources/{userId}",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
