"""
Heart Health Module - DeepAgent Routes
Cardia conversational interface and DeepAgent orchestrator endpoints
Includes voice agent with ElevenLabs TTS
"""
import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.database import get_db, SessionLocal
from services.deep_agent import deep_agent
from services.voice_service import voice_service
import io

router = APIRouter(prefix="/agent", tags=["DeepAgent / Cardia"])


class ChatRequest(BaseModel):
    """Simple chat request — no auth required for dashboard use."""
    message: str
    user_id: int = 1
    user_name: Optional[str] = None


@router.websocket("/chat")
async def ws_agent_chat(ws: WebSocket):
    """
    WebSocket for real-time Cardia conversation.
    Send JSON: {"message": "...", "user_id": 1}
    Receive JSON: AgentResponse
    """
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            message = data.get("message", "")
            user_id = data.get("user_id", 1)
            user_name = data.get("user_name")

            db = SessionLocal()
            try:
                result = await deep_agent.process_message(
                    user_id, message, db, user_name
                )
                await ws.send_json(result)
            finally:
                db.close()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"error": str(e)})
        except Exception:
            pass


@router.post("/command")
async def api_agent_command(data: ChatRequest, db: Session = Depends(get_db)):
    """
    Single-turn text command to DeepAgent.
    No auth required — dashboard uses this directly.
    """
    result = await deep_agent.process_message(
        data.user_id, data.message, db, data.user_name
    )
    return result


@router.get("/context/{user_id}")
def api_get_context(user_id: int):
    """Get current conversation context for a user."""
    return deep_agent.get_context(user_id)


# ═══════════════════════════════════════════
# Voice Agent Endpoints (ElevenLabs TTS)
# ═══════════════════════════════════════════

@router.post("/voice")
async def api_voice_command(data: ChatRequest, db: Session = Depends(get_db)):
    """
    Voice command endpoint: processes message through DeepAgent,
    then converts response to speech via ElevenLabs.
    Returns JSON with text response + base64 audio.
    No auth required — dashboard uses this directly.
    """
    import base64

    # Get text response from DeepAgent
    result = await deep_agent.process_message(
        data.user_id, data.message, db, data.user_name
    )

    # Convert to speech
    audio_bytes = await voice_service.text_to_speech(result["response"])

    response_data = {
        **result,
        "has_audio": audio_bytes is not None,
        "audio_base64": base64.b64encode(audio_bytes).decode() if audio_bytes else None,
        "audio_format": "audio/mpeg" if audio_bytes else None,
    }

    return response_data


@router.post("/tts")
async def api_text_to_speech(data: ChatRequest):
    """
    Pure TTS endpoint: converts text to speech audio.
    Returns MP3 audio stream.
    """
    audio_bytes = await voice_service.text_to_speech(data.message)

    if not audio_bytes:
        return {"error": "TTS service unavailable", "has_audio": False}

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=cardia_voice.mp3"}
    )


@router.get("/voice/status")
async def api_voice_status():
    """Check if voice service is available."""
    return {
        "voice_enabled": voice_service.enabled,
        "provider": "elevenlabs" if voice_service.enabled else None,
    }
