"""
Heart Health Module - Heart Sound Analysis Routes
Audio upload, feature extraction, classification, and LLM-enhanced explanation
"""
import os
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from models.database import get_db
from services.heart_sound_service import analyze_heart_sound, save_heart_sound
from services.llm_service import llm_service
from api.deps import get_current_user
import config

router = APIRouter(prefix="/analyze", tags=["Heart Sound Analysis"])


@router.post("/heart-sound")
async def api_analyze_heart_sound(
    file: UploadFile = File(..., description="Heart sound audio file (WAV/MP3)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Analyze a heart sound recording.
    Accepts WAV or MP3 audio files (10-60 seconds).
    Returns classification, confidence, and LLM-enhanced explanation.
    """
    user_id = user.id if user else 1

    # Save uploaded file
    ext = os.path.splitext(file.filename)[1] if file.filename else ".wav"
    filename = f"heartsound_{user_id}_{int(datetime.utcnow().timestamp())}{ext}"
    file_path = os.path.join(config.UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    audio_url = f"/uploads/{filename}"

    # Step 1: Acoustic feature extraction + classification
    analysis = analyze_heart_sound(file_path)

    # Step 2: Enhance with LLM for richer explanation
    llm_explanation = await llm_service.analyze_report_with_llm(
        report_type="Heart Sound / Auscultation Audio",
        raw_text=f"Audio file analyzed: {filename}",
        extracted_data={
            "classification": analysis["classification"],
            "confidence": analysis["confidence"],
            "is_normal": analysis["is_normal"],
            "features": analysis.get("features", {}),
            "explanation": analysis["explanation"],
        }
    )

    if llm_explanation:
        analysis["jarvis_response"] = llm_explanation
    else:
        # Fallback
        name = user.full_name if user else None
        n = f" {name}" if name else ""
        conf = round(analysis["confidence"] * 100)
        if analysis["is_normal"]:
            analysis["jarvis_response"] = (
                f"Great news{n}! Your heart sound analysis shows: "
                f"{analysis['classification']} ({conf}% confidence). "
                "Sounds healthy! 💚"
            )
        else:
            analysis["jarvis_response"] = (
                f"Hey{n}, your heart sound shows: "
                f"{analysis['classification']} ({conf}% confidence). "
                f"{analysis.get('recommendation', 'Consider consulting a cardiologist.')} 🩺"
            )

    # Save to database
    recording = save_heart_sound(db, user_id, analysis, audio_url)
    analysis["recording_id"] = recording.id

    return analysis


@router.get("/heart-sound/history/{user_id}")
def api_heart_sound_history(user_id: int, limit: int = 10,
                            db: Session = Depends(get_db)):
    """Get heart sound analysis history."""
    from models.db_models import HeartSoundRecording
    from sqlalchemy import desc
    recordings = db.query(HeartSoundRecording).filter(
        HeartSoundRecording.user_id == user_id
    ).order_by(desc(HeartSoundRecording.timestamp)).limit(limit).all()

    return [{
        "id": r.id,
        "classification": r.classification,
        "confidence": r.confidence,
        "explanation": r.explanation,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
    } for r in recordings]
