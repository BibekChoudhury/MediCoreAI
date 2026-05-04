"""
Heart Health Module - Data Source Base Class
Abstract interface that all data source connectors must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BaseDataSource(ABC):
    """Abstract data source interface."""

    def __init__(self, user_id: int, config: Optional[dict] = None):
        self.user_id = user_id
        self.config = config or {}
        self.is_connected = False
        self.last_sync: Optional[datetime] = None

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Return the source type identifier."""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data source. Returns True on success."""
        pass

    @abstractmethod
    async def sync(self) -> List[Dict]:
        """Sync latest data from source. Returns list of vitals readings."""
        pass

    @abstractmethod
    async def get_latest(self) -> Optional[Dict]:
        """Get the most recent reading."""
        pass

    @abstractmethod
    async def get_history(self, start: datetime, end: datetime) -> List[Dict]:
        """Get historical readings within a time range."""
        pass

    def get_status(self) -> Dict:
        return {
            "source_type": self.source_type,
            "is_connected": self.is_connected,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "user_id": self.user_id,
        }
