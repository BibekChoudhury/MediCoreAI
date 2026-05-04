"""
Heart Health Module - Manual Entry Handler
Handles manual vitals, symptoms, and medication log entries
"""
from datetime import datetime
from typing import Dict, List, Optional
from services.data_sources.base import BaseDataSource


class ManualEntryHandler(BaseDataSource):
    """Handles manual health data entry from users."""

    @property
    def source_type(self) -> str:
        return "manual"

    def __init__(self, user_id: int, config_data: Optional[dict] = None):
        super().__init__(user_id, config_data)
        self._entries: List[Dict] = []

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def sync(self) -> List[Dict]:
        return self._entries[-20:]  # Return last 20 entries

    async def get_latest(self) -> Optional[Dict]:
        return self._entries[-1] if self._entries else None

    async def get_history(self, start: datetime, end: datetime) -> List[Dict]:
        return [
            e for e in self._entries
            if start.isoformat() <= e.get("timestamp", "") <= end.isoformat()
        ]

    def add_entry(self, data: Dict) -> Dict:
        """Add a manual health entry."""
        entry = {
            "heart_rate": data.get("heart_rate"),
            "blood_pressure_systolic": data.get("blood_pressure_systolic"),
            "blood_pressure_diastolic": data.get("blood_pressure_diastolic"),
            "spo2": data.get("spo2"),
            "symptoms": data.get("symptoms", []),
            "medications_taken": data.get("medications_taken", []),
            "exercise_minutes": data.get("exercise_minutes"),
            "weight_kg": data.get("weight_kg"),
            "notes": data.get("notes"),
            "source": "manual",
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._entries.append(entry)
        self.last_sync = datetime.utcnow()
        return entry
