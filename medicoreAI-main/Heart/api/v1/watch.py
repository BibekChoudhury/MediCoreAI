"""
Heart Health Module - Watch Data Routes
Smartwatch data retrieval and demo data generation
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models.database import get_db
from services.watch_service import get_latest_watch_data, get_watch_history, generate_demo_data
from api.deps import get_current_user

router = APIRouter(prefix="/watch", tags=["Smartwatch"])


@router.get("/data/{user_id}")
def api_watch_data(user_id: int,
                   start: str = Query(None, description="ISO format start time"),
                   end: str = Query(None, description="ISO format end time"),
                   limit: int = Query(100, le=1000),
                   db: Session = Depends(get_db)):
    """Get historical watch data with optional time range."""
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    data = get_watch_history(db, user_id, start_dt, end_dt, limit)
    return {"count": len(data), "data": data}


@router.get("/latest/{user_id}")
def api_watch_latest(user_id: int, db: Session = Depends(get_db)):
    """Get latest watch reading."""
    data = get_latest_watch_data(db, user_id)
    if not data:
        return {"message": "No watch data available"}
    return {"data": data}


@router.post("/demo/{user_id}")
def api_generate_demo(user_id: int, days: int = Query(7, le=30),
                      db: Session = Depends(get_db)):
    """Generate demo watch data for testing (simulated Firebolt)."""
    count = generate_demo_data(db, user_id, days)
    return {"message": f"Generated {count} data points for {days} days", "count": count}
