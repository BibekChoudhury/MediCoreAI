"""
Heart Health Module - Angiography Report Analysis Routes
PDF extraction + LLM-enhanced explanations (mirroring ECG analysis)
"""
import os
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from models.database import get_db
from services.angioplasty_service import analyze_angioplasty_report, save_angioplasty_report
from services.llm_service import llm_service
from api.deps import get_current_user
import config

router = APIRouter(prefix="/analyze", tags=["Angiography Analysis"])


@router.post("/angiography/pdf")
async def api_analyze_angiography_pdf(
    file: UploadFile = File(..., description="PDF angiography report"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Analyze an angiography procedure report from PDF.
    Follows same pattern as ECG analysis:
    1. Extract text from PDF
    2. Pattern-based structural analysis
    3. LLM enhancement for richer context
    4. Save to database with narration
    """
    if not file.filename or not file.filename.endswith('.pdf'):
        return {"error": "Please upload a PDF file only"}
    
    user_id = user.id if user else 1
    raw_text = ""
    file_url = None
    file_type = "application/pdf"
    
    # Step 1: Extract text from PDF
    try:
        import pypdf
        content = await file.read()
        from io import BytesIO
        pdf_reader = pypdf.PdfReader(BytesIO(content))
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                raw_text += extracted + "\n"
    except ImportError:
        # Fallback to pdfplumber
        try:
            import pdfplumber
            content = await file.read()
            from io import BytesIO
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        raw_text += extracted + "\n"
        except Exception as e:
            return {"error": f"Could not extract PDF text. Ensure pypdf is installed: pip install pypdf. Error: {str(e)}"}
    
    if not raw_text.strip():
        return {"error": "PDF appears to be empty or contains no extractable text"}
    
    # Save the PDF file
    ext = ".pdf"
    filename = f"angiography_{user_id}_{int(datetime.utcnow().timestamp())}{ext}"
    file_path = os.path.join(config.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_url = f"/uploads/{filename}"
    
    # Step 2: Pattern-based structural analysis (like ECG)
    analysis = analyze_angioplasty_report(raw_text)
    
    # Step 3: Enhance with LLM for richer explanation (like ECG)
    llm_explanation = await llm_service.analyze_report_with_llm(
        report_type="Angiography (Cardiac Catheterization)",
        raw_text=raw_text,
        extracted_data={
            "arteries": analysis.get("artery_locations", []),
            "stents": analysis.get("stent_details", []),
            "complications": analysis.get("complications", []),
            "procedure_success": analysis.get("procedure_success", "unknown"),
            "stenosis": analysis.get("stenosis_percentages", []),
        }
    )

    if llm_explanation:
        analysis["jarvis_response"] = llm_explanation
    else:
        # Fallback narration (like ECG)
        name = user.full_name if user else None
        n = f" {name}" if name else ""
        summary = analysis.get("structured_summary", "Your angiography procedure has been reviewed.")
        explanation = analysis.get("explanation", "Please consult with your cardiologist for detailed interpretation.")
        
        analysis["jarvis_response"] = (
            f"Hey{n}, I've reviewed your angiography report. {summary} {explanation} "
            "Follow your doctor's post-procedure instructions carefully. 💚"
        )
    
    # Step 4: Save to database (like ECG)
    report = save_angioplasty_report(db, user_id, analysis, raw_text)
    analysis["report_id"] = report.id
    analysis["timestamp"] = report.date.isoformat() if hasattr(report, 'date') and report.date is not None else None
    analysis["file_url"] = file_url

    return analysis


@router.get("/angiography/history/{user_id}")
def api_angiography_history(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get angiography analysis history for a user (mirrors ECG history)."""
    from models.db_models import AngioplastyReport
    from sqlalchemy import desc
    
    reports = db.query(AngioplastyReport).filter(
        AngioplastyReport.user_id == user_id
    ).order_by(desc(AngioplastyReport.date)).limit(limit).all()

    return [{
        "id": r.id,
        "summary": r.structured_summary,
        "stent_details": r.stent_details,
        "artery_locations": r.artery_locations,
        "complications": r.complications,
        "explanation": r.explanation,
        "timestamp": r.date.isoformat() if r.date else None,
    } for r in reports]
