"""
Heart Health Module - Watch Service
Smartwatch data management and Firebolt integration (simulated)
"""
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.db_models import WatchData, DataSource


def register_watch(db: Session, user_id: int, watch_type: str = "firebolt",
                   config: Optional[dict] = None) -> DataSource:
    """Register a smartwatch data source."""
    source = DataSource(
        user_id=user_id,
        source_type=watch_type,
        status="active",
        config=config or {},
        last_sync=datetime.utcnow(),
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def get_latest_watch_data(db: Session, user_id: int) -> Optional[Dict]:
    """Get the most recent watch data."""
    entry = db.query(WatchData).filter(
        WatchData.user_id == user_id
    ).order_by(desc(WatchData.timestamp)).first()

    if not entry:
        return None

    return {
        "heart_rate": entry.heart_rate,
        "hrv": entry.hrv,
        "spo2": entry.spo2,
        "steps": entry.steps,
        "sleep_stage": entry.sleep_stage,
        "source": entry.source,
        "timestamp": entry.timestamp.isoformat() if entry.timestamp is not None else None,
    }


def get_watch_history(db: Session, user_id: int,
                      start: Optional[datetime] = None, end: Optional[datetime] = None,
                      limit: int = 100) -> List[Dict]:
    """Get historical watch data."""
    query = db.query(WatchData).filter(WatchData.user_id == user_id)
    if start:
        query = query.filter(WatchData.timestamp >= start)
    if end:
        query = query.filter(WatchData.timestamp <= end)

    entries = query.order_by(desc(WatchData.timestamp)).limit(limit).all()

    return [{
        "heart_rate": e.heart_rate,
        "hrv": e.hrv,
        "spo2": e.spo2,
        "steps": e.steps,
        "sleep_stage": e.sleep_stage,
        "source": e.source,
        "timestamp": e.timestamp.isoformat() if e.timestamp is not None else None,
    } for e in entries]


class FireboltSimulator:
    """Simulates Firebolt smartwatch data stream with realistic patterns."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.base_hr = random.randint(60, 80)
        self.base_hrv = random.randint(35, 55)
        self.base_spo2 = random.uniform(96.0, 99.0)
        self.steps = 0
        self.last_update = datetime.utcnow()

    def generate_reading(self) -> Dict:
        """Generate a single realistic vital reading."""
        now = datetime.utcnow()
        hour = now.hour

        # Circadian rhythm simulation
        if 0 <= hour < 6:
            hr_mod = -10  # Lower during sleep
            sleep_stage = random.choice(["deep", "rem", "light", "deep"])
        elif 6 <= hour < 9:
            hr_mod = 5  # Higher on waking
            sleep_stage = random.choice(["awake", "light"])
        elif 12 <= hour < 14:
            hr_mod = 8  # Active midday
            sleep_stage = "awake"
        elif 17 <= hour < 20:
            hr_mod = 12  # Evening activity
            sleep_stage = "awake"
        else:
            hr_mod = 0
            sleep_stage = "awake"

        # Add natural variability
        heart_rate = self.base_hr + hr_mod + random.gauss(0, 3)
        hrv = self.base_hrv + random.gauss(0, 5)
        spo2 = min(100, max(88, self.base_spo2 + random.gauss(0, 0.5)))

        # Steps increment
        if sleep_stage == "awake":
            self.steps += random.randint(0, 50)
        else:
            self.steps += 0

        return {
            "heart_rate": round(max(40, min(180, heart_rate)), 1),
            "hrv": round(max(10, hrv), 1),
            "spo2": round(spo2, 1),
            "steps": self.steps,
            "sleep_stage": sleep_stage,
            "source": "firebolt",
            "timestamp": now.isoformat(),
        }


def generate_demo_data(db: Session, user_id: int, days: int = 7) -> int:
    """Generate demo watch data for testing."""
    simulator = FireboltSimulator(user_id)
    now = datetime.utcnow()
    count = 0

    for day_offset in range(days, 0, -1):
        base_time = now - timedelta(days=day_offset)
        simulator.steps = 0

        # Generate readings every 15 minutes
        for minute_offset in range(0, 1440, 15):
            ts = base_time + timedelta(minutes=minute_offset)
            reading = simulator.generate_reading()

            entry = WatchData(
                user_id=user_id,
                source="firebolt",
                timestamp=ts,
                heart_rate=reading["heart_rate"],
                hrv=reading["hrv"],
                spo2=reading["spo2"],
                steps=reading["steps"],
                sleep_stage=reading["sleep_stage"],
            )
            db.add(entry)
            count += 1

        if count % 500 == 0:
            db.commit()

    db.commit()
    return count
