"""
Heart Health Module - ECG Analysis Routes
Upload and analyze ECG reports with LLM-enhanced explanations
"""
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.database import get_db
from services.ecg_service import analyze_ecg_text, save_ecg_report
from services.llm_service import llm_service
from api.deps import get_current_user
import config

router = APIRouter(prefix="/analyze", tags=["ECG Analysis"])


@router.post("/ecg")
async def api_analyze_ecg(
    file: UploadFile = File(None),
    text: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Analyze an ECG report.
    Accepts: image upload (JPEG/PNG), PDF, or raw text.
    Returns: analysis with findings, explanation, and Cardia narration.
    """
    user_id = user.id if user else 1
    raw_text = text or ""
    file_url = None
    file_type = None

    # Handle file upload
    if file:
        file_type = file.content_type or "unknown"
        ext = os.path.splitext(file.filename)[0] if file.filename else ""
        ext = os.path.splitext(file.filename)[1] if file.filename else ".bin"
        filename = f"ecg_{user_id}_{int(datetime.utcnow().timestamp())}{ext}"
        file_path = os.path.join(config.UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_url = f"/uploads/{filename}"

        # For text-based files, read content
        if ext.lower() in (".txt", ".text"):
            try:
                raw_text = content.decode("utf-8")
            except Exception:
                pass
        elif ext.lower() in (".pdf", ".jpg", ".jpeg", ".png"):
            # For image/PDF uploads without accompanying text
            if not raw_text:
                raw_text = (
                    "ECG image/PDF uploaded. No machine-readable text available. "
                    "Please provide the ECG report text for accurate analysis, "
                    "or describe the key findings from the report."
                )

    if not raw_text:
        return {"error": "Please provide ECG text or upload a file for analysis."}

    # Step 1: Keyword-based pattern analysis
    analysis = analyze_ecg_text(raw_text)

    # Step 2: Enhance with LLM for richer explanation
    llm_explanation = await llm_service.analyze_report_with_llm(
        report_type="ECG (Electrocardiogram)",
        raw_text=raw_text,
        extracted_data={
            "findings": analysis["findings"],
            "severity": analysis["severity"],
            "is_normal": analysis["is_normal"],
            "risk_flags": analysis["risk_flags"],
        }
    )

    if llm_explanation:
        analysis["jarvis_response"] = llm_explanation
    else:
        # Fallback to simple narration
        name = user.full_name if user else None
        n = f" {name}" if name else ""
        if analysis["is_normal"]:
            analysis["jarvis_response"] = (
                f"Good news{n}! Your ECG looks normal — regular rhythm, no red flags. "
                "Keep up the healthy habits! 💚"
            )
        else:
            findings = ", ".join(analysis["findings"][:3])
            analysis["jarvis_response"] = (
                f"Hey{n}, I found a few things worth noting: {findings}. "
                "I've included detailed explanations above. "
                "I'd recommend sharing these results with your cardiologist for a proper evaluation. 🩺"
            )

    # Save to database
    report = save_ecg_report(db, user_id, analysis, file_url, file_type, raw_text)
    analysis["report_id"] = report.id
    analysis["timestamp"] = report.timestamp.isoformat() if report.timestamp else None

    return analysis


@router.get("/ecg/history/{user_id}")
def api_ecg_history(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get ECG analysis history for a user."""
    from models.db_models import ECGReport
    from sqlalchemy import desc
    reports = db.query(ECGReport).filter(
        ECGReport.user_id == user_id
    ).order_by(desc(ECGReport.timestamp)).limit(limit).all()

    return [{
        "id": r.id,
        "summary": r.summary,
        "findings": r.findings,
        "risk_flags": r.risk_flags,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
    } for r in reports]
