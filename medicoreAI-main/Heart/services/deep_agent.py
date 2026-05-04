"""
Heart Health Module - DeepAgent Orchestrator
Central intelligence layer that coordinates all services, manages context,
and generates dynamic LLM-powered responses through Cardia
"""
from typing import Optional
from sqlalchemy.orm import Session
from services.jarvis_personality import jarvis
from services.context_engine import context_engine
from services.prediction_service import predict_heart_risk
from services.monitoring_service import get_latest_vitals, generate_health_summary
from services.alert_service import check_alerts
from services.llm_service import llm_service


class DeepAgent:
    """
    Core orchestrator that:
    - Detects user intent from messages
    - Routes to appropriate services to fetch real data
    - Sends data + intent to LLM for natural, conversational responses
    - Falls back to template responses if LLM is unavailable
    """

    def __init__(self):
        self.jarvis = jarvis
        self.context = context_engine
        self.llm = llm_service

    async def process_message(self, user_id: int, message: str, db: Session,
                              user_name: Optional[str] = None) -> dict:
        """Main entry point: process a user message and return a response."""
        session = self.context.get_or_create_session(user_id)
        if user_name:
            session.user_preferences["name"] = user_name

        name = session.user_preferences.get("name")

        # Detect intent and emotional state
        intent = self.context.detect_intent(message)
        emotional_state = self.context.detect_emotional_state(message)
        session.set_emotional_state(emotional_state)
        session.add_turn("user", message, intent)
        session.add_topic(intent)

        # Route to appropriate handler
        response_data = await self._route_intent(
            intent, message, user_id, name, db, session
        )

        # Record assistant response
        session.add_turn("assistant", response_data["response"], intent)

        return response_data

    async def _route_intent(self, intent: str, message: str, user_id: int,
                            name: Optional[str], db: Session, session) -> dict:
        """Route detected intent to fetch data, then generate LLM response."""

        # Step 1: Fetch relevant data based on intent
        health_data, extra_context, suggestions = await self._fetch_intent_data(
            intent, message, user_id, name, db
        )

        # Step 2: Generate LLM response with context
        llm_response = await self.llm.generate_contextual_response(
            user_message=message,
            intent=intent,
            health_data=health_data,
            conversation_history=session.conversation_history[-6:] if session else None,
            user_name=name,
            extra_context=extra_context
        )

        # Step 3: Fall back to template if LLM fails
        if llm_response:
            response = llm_response
        else:
            response = await self._fallback_response(intent, message, user_id, name, db, health_data)

        return {
            "response": response,
            "intent_detected": intent,
            "data": health_data,
            "suggestions": suggestions,
            "emotional_tone": session.emotional_state if session else "calm"
        }

    async def _fetch_intent_data(self, intent, message, user_id, name, db):
        """Fetch relevant data from services based on intent."""
        health_data = None
        extra_context = ""
        suggestions = [
            "Check my heart health 💓",
            "Show my vitals 📊",
            "Upload a report 📋",
            "Help me out! 🤝"
        ]

        if intent == "greeting":
            health_data = get_latest_vitals(db, user_id)
            extra_context = "User is greeting you. Be warm and friendly. Include a brief health status if data is available."
            suggestions = [
                "Check my risk 🎯",
                "Show my vitals 📊",
                "Upload a report 📋",
                "Connect my device 📱"
            ]

        elif intent == "predict":
            health_data = get_latest_vitals(db, user_id)
            extra_context = (
                "User wants a heart risk prediction. If you have their vitals data, comment on it. "
                "Guide them to the Risk Scan tab to enter clinical data for a full ML prediction. "
                "Explain what data is needed (age, BP, cholesterol, etc.)."
            )
            suggestions = [
                "Use my latest vitals",
                "I'll enter manually",
                "What data do you need?"
            ]

        elif intent == "monitor":
            health_data = get_latest_vitals(db, user_id)
            extra_context = (
                "User is asking about their vitals/monitoring. Analyze the health data provided and give insights. "
                "Comment on heart rate, SpO2, HRV if available. Flag anything abnormal."
            )
            suggestions = [
                "Show weekly trends 📈",
                "Set up alerts ⚡",
                "Connect a device 📱"
            ]

        elif intent == "ecg":
            extra_context = (
                "User is asking about ECG analysis. Guide them to upload their ECG report "
                "in the Reports tab. Explain what you can detect (AFib, ST changes, etc.)."
            )
            suggestions = ["Upload ECG report 📋", "What can you detect?"]

        elif intent == "angiography":
            extra_context = (
                "User is asking about angiography reports. Guide them to upload PDF or paste their report text "
                "in the Reports tab. Explain you can extract stent details, arteries, complications."
            )
            suggestions = ["Upload angiography PDF 📄", "What is angiography? 🤔"]

        elif intent == "heart_sound":
            extra_context = (
                "User is asking about heart sound analysis. Guide them to upload audio "
                "(WAV/MP3) in the Reports tab. Explain you check for murmurs, gallops, rhythm."
            )
            suggestions = ["Upload heart sound 🎵", "What sounds are abnormal?"]

        elif intent == "history":
            summary = generate_health_summary(db, user_id)
            health_data = summary
            extra_context = "User wants health history/trends. Summarize any available data."
            suggestions = ["Show weekly heart rate 📈", "Show monthly trends 📊"]

        elif intent == "alert":
            extra_context = (
                "User wants to set up health alerts. Explain you can monitor heart rate, "
                "SpO2, and other vitals with configurable thresholds."
            )
            suggestions = ["Set heart rate alert 💓", "Set SpO2 alert 🫁"]

        elif intent == "data_source":
            extra_context = (
                "User wants to connect a health data source. Currently supported: "
                "Google Fit (with OAuth), and Manual Entry. "
                "Fitbit and Firebolt Watch are coming soon."
            )
            suggestions = [
                "Connect Google Fit 📱",
                "Enter manually ✍️"
            ]

        elif intent == "medication":
            extra_context = (
                "User is asking about medication. Remind them you can't prescribe medication "
                "but can help track what they're taking."
            )
            suggestions = ["Log a medication 💊", "Set a reminder ⏰"]

        elif intent == "emergency":
            health_data = get_latest_vitals(db, user_id)
            extra_context = (
                "⚠️ EMERGENCY: User may be experiencing a cardiac emergency. "
                "Respond with URGENT instructions: Call emergency services (108/911/112), "
                "sit down, chew aspirin if not allergic, loosen clothing. "
                "Be very direct and caring. Include their vitals if available."
            )
            suggestions = []

        elif intent == "help":
            extra_context = (
                "User wants to know what you can do. List your capabilities: "
                "heart risk prediction, ECG analysis, angiography report analysis, "
                "heart sound analysis, live vital monitoring, device connection, alerts."
            )
            suggestions = [
                "Check my heart risk 🎯",
                "Show my vitals 📊",
                "Upload a report 📋",
                "Connect a device 📱"
            ]

        else:  # general
            health_data = get_latest_vitals(db, user_id)
            extra_context = (
                "User is asking a general question. Answer naturally and helpfully. "
                "If the question is health-related, provide accurate information. "
                "If you have their health data, reference it when relevant."
            )

        return health_data, extra_context, suggestions

    async def _fallback_response(self, intent, message, user_id, name, db, health_data):
        """Template-based fallback when LLM is unavailable."""
        n = self.jarvis.format_name(name)

        if intent == "greeting":
            if health_data:
                hr = health_data.get('heart_rate', 'N/A')
                return f"Hey{n}! 👋 Your heart's at {hr} bpm — looking good! How can I help you today?"
            return f"Hey{n}! 👋 I'm Cardia, your heart health buddy. What's on your mind?"

        elif intent == "emergency":
            return (
                f"🚨 STAY CALM{n.upper()} 🚨\n\n"
                "1. CALL 108 (India) / 911 (US) / 112 (EU) NOW\n"
                "2. Sit or lie down\n"
                "3. Chew an aspirin if not allergic\n"
                "4. Loosen tight clothing\n\n"
                "Help is on the way. I'm here with you ❤️"
            )

        elif intent == "monitor":
            if health_data:
                hr = health_data.get("heart_rate", "N/A")
                spo2 = health_data.get("spo2", "N/A")
                return f"Here's your latest{n}: HR {hr} bpm, SpO2 {spo2}%. Everything looks steady! 💚"
            return f"I don't have your vitals yet{n}. Connect a device or enter them manually!"

        elif intent == "predict":
            return f"Let's check your risk{n}! Head to the Risk Scan tab and fill in your clinical data. I'll crunch the numbers! 🎯"

        elif intent == "help":
            return (
                f"Hey{n}! Here's what I can do:\n"
                "🫀 Heart Risk Check\n📊 Live Vitals Monitoring\n"
                "📋 ECG Analysis\n🩺 Angioplasty Reports\n"
                "🎧 Heart Sound Check\n📱 Device Connection\n"
                "Just ask me anything! 💪"
            )

        else:
            return self.jarvis.general_response(name)

    def get_context(self, user_id: int) -> dict:
        session = self.context.get_session(user_id)
        if session:
            return session.to_dict()
        return {"message": "No active session found"}


# Singleton instance
deep_agent = DeepAgent()
