"""
Heart Health Module - Data Fusion Engine
Priority-based multi-source data merging with conflict resolution
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from services.data_sources.base import BaseDataSource
from services.data_sources.google_fit import GoogleFitConnector
from services.data_sources.fitbit_connector import FitbitConnector
from services.data_sources.firebolt import FireboltConnector
from services.data_sources.manual_entry import ManualEntryHandler


# Priority: higher number = higher priority
DEFAULT_PRIORITIES = {
    "firebolt": 5,
    "fitbit": 4,
    "google_fit": 3,
    "manual": 2,
    "mi_digital": 1,
}

CONNECTOR_MAP = {
    "firebolt": FireboltConnector,
    "google_fit": GoogleFitConnector,
    "fitbit": FitbitConnector,
    "manual": ManualEntryHandler,
}


class DataFusionEngine:
    """
    Merges data from multiple health sources using priority-based resolution.
    When metrics conflict, higher-priority sources win.
    """

    def __init__(self):
        self._connectors: Dict[int, Dict[str, BaseDataSource]] = {}

    def register_source(self, user_id: int, source_type: str,
                       config: Optional[dict] = None, priority: Optional[int] = None) -> Dict:
        """Register a new data source for a user."""
        if user_id not in self._connectors:
            self._connectors[user_id] = {}

        connector_cls = CONNECTOR_MAP.get(source_type)
        if not connector_cls:
            return {"error": f"Unknown source type: {source_type}"}

        connector = connector_cls(user_id, config)
        self._connectors[user_id][source_type] = connector

        return {
            "source_type": source_type,
            "status": "registered",
            "priority": priority or DEFAULT_PRIORITIES.get(source_type, 1),
        }

    def get_sources(self, user_id: int) -> List[Dict]:
        """Get all registered sources for a user."""
        sources = self._connectors.get(user_id, {})
        result = []
        for source_type, connector in sources.items():
            status = connector.get_status()
            status["priority"] = DEFAULT_PRIORITIES.get(source_type, 1)
            result.append(status)
        return result

    async def sync_all(self, user_id: int) -> Dict:
        """Sync all connected sources and return fused data."""
        from models.database import SessionLocal
        from models.db_models import DataSource as DS
        
        # Load sources from database to get latest configs (like tokens)
        db = SessionLocal()
        try:
            db_sources = db.query(DS).filter(DS.user_id == user_id, DS.status == "active").all()  # type: ignore
            
            # Ensure connectors are up-to-date with database configs
            for db_source in db_sources:
                source_type = db_source.source_type  # type: ignore
                if source_type not in self._connectors.get(user_id, {}):  # type: ignore
                    # Create new connector with config from DB
                    connector_cls = CONNECTOR_MAP.get(source_type)  # type: ignore
                    if connector_cls:
                        connector = connector_cls(user_id, db_source.config)  # type: ignore
                        if user_id not in self._connectors:
                            self._connectors[user_id] = {}
                        self._connectors[user_id][source_type] = connector  # type: ignore
                else:
                    # Update existing connector with latest config (tokens, etc.)
                    connector = self._connectors[user_id][source_type]  # type: ignore
                    config = db_source.config  # type: ignore
                    if config:  # type: ignore
                        if hasattr(connector, 'access_token') and 'access_token' in config:  # type: ignore
                            connector.access_token = config.get('access_token')  # type: ignore
                            connector.refresh_token = config.get('refresh_token')  # type: ignore
        finally:
            db.close()
        
        sources = self._connectors.get(user_id, {})
        all_data = {}
        sync_results = []

        for source_type, connector in sources.items():
            try:
                if not connector.is_connected:
                    await connector.connect()

                data = await connector.sync()
                priority = DEFAULT_PRIORITIES.get(source_type, 1)

                for reading in data:
                    ts = reading.get("timestamp", datetime.utcnow().isoformat())
                    if ts not in all_data or priority > all_data[ts].get("_priority", 0):
                        all_data[ts] = {**reading, "_priority": priority}

                # After sync, if tokens were refreshed (for Google Fit), save them back to DB
                if source_type == "google_fit" and hasattr(connector, 'access_token') and connector.access_token:  # type: ignore
                    db = SessionLocal()
                    try:
                        from models.db_models import DataSource as DS
                        db_source = db.query(DS).filter(  # type: ignore
                            DS.user_id == user_id,  # type: ignore
                            DS.source_type == "google_fit"  # type: ignore
                        ).first()  # type: ignore
                        if db_source:  # type: ignore
                            db_source.config = {  # type: ignore
                                "access_token": connector.access_token,  # type: ignore
                                "refresh_token": connector.refresh_token,  # type: ignore
                                "token_type": "Bearer"
                            }
                            db.commit()  # type: ignore
                    except Exception as e:  # type: ignore
                        print(f"⚠️  Failed to save refreshed token: {e}")  # type: ignore
                    finally:
                        db.close()  # type: ignore

                sync_results.append({
                    "source": source_type,
                    "status": "success",
                    "readings": len(data)
                })

            except Exception as e:
                sync_results.append({
                    "source": source_type,
                    "status": "error",
                    "error": str(e)
                })

        # Clean up priority field
        fused_readings = []
        for ts, reading in sorted(all_data.items()):
            reading.pop("_priority", None)
            fused_readings.append(reading)

        return {
            "total_readings": len(fused_readings),
            "sync_results": sync_results,
            "latest": fused_readings[-1] if fused_readings else None,
        }

    async def get_fused_latest(self, user_id: int) -> Optional[Dict]:
        """Get the latest fused reading from highest-priority source."""
        sources = self._connectors.get(user_id, {})
        best_reading = None
        best_priority = -1

        for source_type, connector in sources.items():
            priority = DEFAULT_PRIORITIES.get(source_type, 1)
            if priority > best_priority:
                try:
                    reading = await connector.get_latest()
                    if reading:
                        best_reading = reading
                        best_priority = priority
                except Exception:
                    continue

        return best_reading


# Singleton
data_fusion = DataFusionEngine()
