"""
Heart Health Module - Voice Service
ElevenLabs Text-to-Speech integration for HEART voice agent
"""
import httpx
import config
from typing import Optional


class VoiceService:
    """
    ElevenLabs TTS service for converting HEART responses to speech.
    Uses the ElevenLabs v1 API for high-quality voice synthesis.
    """

    # Rachel voice — warm, friendly, clear female voice
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
    # Alternative voices:
    # "EXAVITQu4vr4xnSDxMaL" = Bella (friendly female)
    # "ErXwobaYiN019PkySvjV" = Antoni (friendly male)
    # "pNInz6obpgDQGcFmaJgB" = Adam (deep male)

    VOICE_SETTINGS = {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.4,
        "use_speaker_boost": True,
    }

    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = self.DEFAULT_VOICE_ID
        self.enabled = bool(self.api_key)

    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs API.
        Returns raw audio bytes (MP3 format).
        """
        if not self.enabled:
            return None

        vid = voice_id or self.voice_id
        url = f"{self.base_url}/text-to-speech/{vid}"

        # Strip emojis and markdown for cleaner speech
        clean_text = self._clean_for_speech(text)

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        payload = {
            "text": clean_text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": self.VOICE_SETTINGS,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.content
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return None

    async def get_voices(self) -> list:
        """List available ElevenLabs voices."""
        if not self.enabled:
            return []

        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return [
                    {"voice_id": v["voice_id"], "name": v["name"]}
                    for v in data.get("voices", [])
                ]
        except Exception as e:
            print(f"ElevenLabs voice list error: {e}")
            return []

    def _clean_for_speech(self, text: str) -> str:
        """Clean text for better TTS output — remove emojis, markdown, etc."""
        import re

        # Remove emoji characters
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols
            "\U0001F680-\U0001F6FF"  # transport
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002600-\U000027BF"
            "\U0000FE00-\U0000FE0F"
            "\U0001F900-\U0001F9FF"
            "]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub("", text)

        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)       # italic
        text = re.sub(r'#{1,6}\s*', '', text)           # headers
        text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)  # bullets
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # links

        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        # Truncate very long texts (ElevenLabs has limits)
        if len(text) > 2500:
            text = text[:2500] + "... I'll keep the rest short."

        return text


# Singleton instance
voice_service = VoiceService()
