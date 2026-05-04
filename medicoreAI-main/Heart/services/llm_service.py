"""
Heart Health Module - LLM Service
Handles OpenAI-compatible communication with OpenRouter
Provides contextual, conversational responses for Cardia voice agent
"""
import httpx
import json
import config
from typing import List, Dict, Optional, Any


class LLMService:
    """
    Service to interact with OpenRouter using OpenAI-compatible API.
    Powers Cardia's conversational intelligence across all intents.
    """

    SYSTEM_PROMPT = (
        "You are Cardia, a warm and intelligent AI health assistant specializing in heart health. "
        "You are part of a Heart Health Module that tracks vitals, analyzes ECG/angiography reports, "
        "monitors heart sounds, and predicts cardiac risk.\n\n"
        "PERSONALITY:\n"
        "- Talk like a caring, knowledgeable friend — warm but professional\n"
        "- Use natural language, be concise, and use emojis sparingly but naturally\n"
        "- Explain medical concepts in plain language anyone can understand\n"
        "- Be encouraging and positive, but always honest when something is serious\n"
        "- Show genuine empathy for health concerns\n"
        "- When health data is provided, analyze it and give specific insights\n"
        "- Always remind users to consult a real doctor for serious concerns\n"
        "- Keep responses under 150 words unless explaining something complex\n"
        "- NEVER refuse to discuss health topics — you're a health assistant\n"
        "- If you don't have specific data, say so and suggest how to get it\n"
    )

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.OPENROUTER_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/medicore-ai",
            "X-Title": config.OPENROUTER_APP_NAME,
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Optional[str]:
        """Request a chat completion from OpenRouter."""
        if not self.api_key:
            return None

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LLM error: {str(e)}")
            return None

    async def generate_contextual_response(
        self,
        user_message: str,
        intent: str,
        health_data: Optional[Dict] = None,
        conversation_history: Optional[List] = None,
        user_name: Optional[str] = None,
        extra_context: str = ""
    ) -> Optional[str]:
        """
        Generate a contextual LLM response using intent + health data.
        This is the main method used by DeepAgent for ALL intents.
        """
        # Build context block
        context_parts = []

        if user_name:
            context_parts.append(f"User's name: {user_name}")

        context_parts.append(f"Detected intent: {intent}")

        if health_data:
            context_parts.append(f"User's health data:\n{json.dumps(health_data, indent=2, default=str)}")

        if extra_context:
            context_parts.append(extra_context)

        context_block = "\n".join(context_parts)

        system_message = self.SYSTEM_PROMPT + f"\n\nCONTEXT:\n{context_block}"

        messages = [{"role": "system", "content": system_message}]

        # Add conversation history (last 6 turns)
        if conversation_history:
            for turn in conversation_history[-6:]:
                role = turn.get("role", "user")
                msg = turn.get("message", "")
                if role in ("user", "assistant") and msg:
                    messages.append({"role": role, "content": msg})

        messages.append({"role": "user", "content": user_message})

        return await self.chat_completion(messages, max_tokens=500)

    async def analyze_report_with_llm(
        self,
        report_type: str,
        raw_text: str,
        extracted_data: Dict,
        max_tokens: int = 800
    ) -> Optional[str]:
        """
        Use LLM to generate intelligent analysis of ECG/Angiography/Heart Sound reports.
        Takes the structured extraction as context and generates a rich explanation.
        """
        system = (
            "You are Cardia, a medical AI assistant specializing in cardiology. "
            "You are analyzing a medical report. Provide a clear, accurate, patient-friendly explanation. "
            "Be specific about findings, their clinical significance, and recommended next steps. "
            "Use plain language but be medically accurate. Be concise but thorough."
        )

        user_msg = (
            f"Report type: {report_type}\n\n"
            f"Raw report text:\n{raw_text[:2000]}\n\n"
            f"Extracted findings:\n{json.dumps(extracted_data, indent=2, default=str)}\n\n"
            f"Please provide:\n"
            f"1. A clear summary of what this report shows\n"
            f"2. What each finding means in plain language\n"
            f"3. Whether any findings are concerning\n"
            f"4. Recommended next steps"
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ]

        return await self.chat_completion(messages, max_tokens=max_tokens)

    async def get_jarvis_response(
        self,
        user_message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Legacy method — kept for backward compatibility."""
        if not system_prompt:
            system_prompt = self.SYSTEM_PROMPT

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            for turn in context[-5:]:
                role = turn.get("role", "user")
                msg = turn.get("message", turn.get("content", ""))
                if role in ("user", "assistant") and msg:
                    messages.append({"role": role, "content": msg})

        messages.append({"role": "user", "content": user_message})
        return await self.chat_completion(messages)


# Singleton instance
llm_service = LLMService()
