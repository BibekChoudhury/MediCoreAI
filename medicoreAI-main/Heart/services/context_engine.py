"""
Heart Health Module - Context Engine
Session-based conversation memory and user preference tracking
"""
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class ConversationSession:
    """Represents a single user conversation session."""

    def __init__(self, user_id: int, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self.turn_count = 0
        self.recent_topics: List[str] = []
        self.pending_questions: List[str] = []
        self.emotional_state = "calm"
        self.conversation_history: List[dict] = []
        self.last_interaction = datetime.utcnow()
        self.user_preferences = {
            "explanation_depth": "standard",  # brief, standard, detailed
            "alert_sensitivity": "normal",     # low, normal, high
            "name": None,
        }

    def add_turn(self, role: str, message: str, intent: Optional[str] = None):
        self.turn_count += 1
        self.last_interaction = datetime.utcnow()
        self.conversation_history.append({
            "role": role,
            "message": message,
            "intent": intent,
            "timestamp": self.last_interaction.isoformat()
        })
        # Keep last 50 turns
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def add_topic(self, topic: str):
        if topic not in self.recent_topics:
            self.recent_topics.append(topic)
        if len(self.recent_topics) > 10:
            self.recent_topics = self.recent_topics[-10:]

    def set_emotional_state(self, state: str):
        valid_states = ["calm", "concerned", "anxious", "curious", "happy", "emergency"]
        if state in valid_states:
            self.emotional_state = state

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "turn_count": self.turn_count,
            "recent_topics": self.recent_topics,
            "pending_questions": self.pending_questions,
            "emotional_state": self.emotional_state,
            "last_interaction": self.last_interaction.isoformat(),
        }


class ContextEngine:
    """
    Manages conversation contexts across users and sessions.
    In-memory implementation (Redis-ready interface).
    """

    def __init__(self):
        self._sessions: Dict[int, ConversationSession] = {}

    def get_or_create_session(self, user_id: int) -> ConversationSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = ConversationSession(user_id)
        return self._sessions[user_id]

    def get_session(self, user_id: int) -> Optional[ConversationSession]:
        return self._sessions.get(user_id)

    def reset_session(self, user_id: int) -> ConversationSession:
        self._sessions[user_id] = ConversationSession(user_id)
        return self._sessions[user_id]

    def detect_emotional_state(self, message: str) -> str:
        """Basic emotional state detection from message text."""
        message_lower = message.lower()

        emergency_keywords = ["emergency", "chest pain", "can't breathe", "heart attack",
                              "dying", "severe pain", "help me", "911", "ambulance"]
        anxious_keywords = ["worried", "scared", "anxious", "nervous", "afraid",
                           "concern", "panic", "stress"]
        curious_keywords = ["what does", "what is", "explain", "tell me", "how",
                           "why", "mean", "understand"]
        happy_keywords = ["great", "excellent", "happy", "good news", "wonderful",
                         "better", "improved", "thank"]

        if any(kw in message_lower for kw in emergency_keywords):
            return "emergency"
        if any(kw in message_lower for kw in anxious_keywords):
            return "concerned"
        if any(kw in message_lower for kw in happy_keywords):
            return "happy"
        if any(kw in message_lower for kw in curious_keywords):
            return "curious"
        return "calm"

    def detect_intent(self, message: str) -> str:
        """Detect user intent from message text."""
        message_lower = message.lower()

        intent_keywords = {
            "emergency": ["emergency", "chest pain", "heart attack", "can't breathe", "911", "help me"],
            "predict": ["predict", "risk", "assessment", "chance", "probability", "likelihood"],
            "ecg": ["ecg", "ekg", "electrocardiogram", "ecg report"],
            "angiography": ["angiography", "angiogram", "stent", "catheterization", "procedure report"],
            "heart_sound": ["heart sound", "heartbeat", "murmur", "stethoscope", "audio", "recording"],
            "monitor": ["vitals", "heart rate", "blood pressure", "spo2", "oxygen", "monitoring",
                       "how's my heart", "how is my heart", "health status", "how am i"],
            "history": ["history", "trend", "past", "previous", "over time", "weekly", "monthly"],
            "alert": ["alert", "notification", "threshold", "warn me", "notify"],
            "data_source": ["connect", "pair", "google fit", "fitbit", "watch", "wearable", "sync"],
            "medication": ["medicine", "medication", "drug", "pill", "prescription", "dose"],
            "greeting": ["hello", "hi", "hey", "good morning", "good evening", "jarvis",
                         "good afternoon", "what's up"],
            "help": ["help", "what can you", "features", "options", "menu"],
        }

        for intent, keywords in intent_keywords.items():
            if any(kw in message_lower for kw in keywords):
                return intent

        return "general"


# Singleton instance
context_engine = ContextEngine()
