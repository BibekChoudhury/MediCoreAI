import base64
import logging
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, init_db
from models.schemas import AnalysisResponse, ErrorResponse, HealthResponse, MedicineResult
from models.user import User
from routes.auth_routes import auth_router
from routes.profile_routes import profile_router
from services.ai_service import (
    analyze_image_with_groq,
    consult_text_with_groq,
    encode_image_from_bytes,
    text_to_speech_gtts,
    transcribe_audio_with_groq,
)
from services.alternative_service import get_alternative_medicines
from services.disease_service import load_artifacts, load_disease_info, predict_disease
from services.medicine_service import extract_medicine_names
from services.personalization_engine import (
    build_prescription_personalization,
    personalize_consultation_output,
    personalize_disease_prediction,
    personalize_health_report_analysis,
)
from services.health_report_service import analyze_report_with_llm, extract_report_text
from services.ocr_service import extract_text_from_prescription
from utils.helpers import (
    DISCLAIMER,
    MAX_FILE_SIZE_BYTES,
    validate_file_extension,
    validate_file_size,
)
from middleware.auth_middleware import jwt_auth_middleware
from utils.auth_dependencies import get_current_user
from utils.patient_context import (
    format_patient_context_for_prompt,
    get_or_create_patient_profile,
    get_patient_context,
)
from utils.storage import UPLOAD_ROOT, ensure_upload_directories

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.warning("GROQ_API_KEY is not set. API calls will fail.")

# ---------------------------------------------------------------------------
# Load ML artifacts for disease prediction
# ---------------------------------------------------------------------------
artifacts = load_artifacts()
disease_info = load_disease_info()
MODEL = artifacts['model']
LABEL_ENCODER = artifacts['label_encoder']
FEATURE_NAMES: List[str] = artifacts['feature_names']


def _merge_extracted_medications(db: Session, user_id: int, medicine_names: List[str]) -> None:
    profile = get_or_create_patient_profile(db, user_id)
    current = {item.lower(): item for item in (profile.medications or [])}
    for med in medicine_names:
        normalized = med.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key not in current:
            current[key] = normalized
    profile.medications = list(current.values())
    db.add(profile)
    db.commit()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MediCore AI API",
    description="Unified backend: disease prediction, AI consultation, and prescription analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(jwt_auth_middleware)
app.include_router(auth_router)
app.include_router(profile_router)
ensure_upload_directories()
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")

# ---------------------------------------------------------------------------
# Mount Heart Health Module as sub-application
# ---------------------------------------------------------------------------
try:
    heart_module_dir = os.path.join(os.path.dirname(__file__), '..', 'Heart')
    heart_module_dir = os.path.abspath(heart_module_dir)
    if os.path.isdir(heart_module_dir):
        import importlib.util

        # Save original state so we can restore after Heart loads
        _orig_path = sys.path.copy()
        _orig_cwd = os.getcwd()

        # Remove backend dir from path to prevent its packages from shadowing
        backend_dir = os.path.abspath(os.path.dirname(__file__))
        sys.path = [p for p in sys.path if os.path.abspath(p) != backend_dir]
        sys.path.insert(0, heart_module_dir)

        # Remove cached backend modules that share names with Heart modules
        _conflicting_prefixes = ('config', 'models', 'services', 'utils', 'api')
        _saved_mods = {}
        for mod_name in list(sys.modules.keys()):
            for prefix in _conflicting_prefixes:
                if mod_name == prefix or mod_name.startswith(prefix + '.'):
                    _saved_mods[mod_name] = sys.modules.pop(mod_name)
                    break

        try:
            os.chdir(heart_module_dir)
            _heart_spec = importlib.util.spec_from_file_location(
                "heart_main", os.path.join(heart_module_dir, "main.py")
            )
            _heart_mod = importlib.util.module_from_spec(_heart_spec)
            _heart_spec.loader.exec_module(_heart_mod)
            app.mount("/heart", _heart_mod.app)
            logger.info("Heart Health Module mounted at /heart")
        finally:
            os.chdir(_orig_cwd)
            sys.path = _orig_path
            # Restore backend modules
            sys.modules.update(_saved_mods)
    else:
        logger.warning("Heart module directory not found at %s", heart_module_dir)
except Exception as exc:
    logger.warning("Failed to mount Heart Health Module: %s", exc)


@app.on_event("startup")
def on_startup():
    ensure_upload_directories()
    init_db()

# ========================== HEALTH ==========================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "loaded_features": len(FEATURE_NAMES),
        "ai_available": True,
    }

# ========================== HEART MODULE REDIRECTS ==========================
# Backward-compatibility redirects so existing integrations (Android Health
# Sync Pro app, Google Fit OAuth) keep working with the old (pre-mount) paths.

from fastapi.responses import RedirectResponse
from fastapi import Request as FastRequest

@app.api_route("/api/v1/data/health/submit", methods=["POST"])
async def redirect_health_submit(request: FastRequest):
    """Redirect Health Sync Pro app POST to Heart sub-app."""
    return RedirectResponse(
        url="/heart/api/v1/data/health/submit",
        status_code=307  # 307 preserves POST method
    )

@app.get("/api/v1/data/callback/google-fit")
async def redirect_google_fit_callback(request: FastRequest):
    """Redirect Google Fit OAuth callback to Heart sub-app."""
    query_string = str(request.url.query)
    redirect_url = f"/heart/api/v1/data/callback/google-fit?{query_string}" if query_string else "/heart/api/v1/data/callback/google-fit"
    return RedirectResponse(url=redirect_url, status_code=307)


@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    return HealthResponse(status="ok", message="MediCore AI API is running.")

# ========================== DISEASE PREDICTION ==============================

class PredictRequest(BaseModel):
    symptoms: List[str]


@app.get("/api/symptoms")
async def api_symptoms():
    return {"symptoms": FEATURE_NAMES}


@app.get("/api/metadata")
async def api_metadata():
    meta = artifacts['meta']
    return {
        "model_timestamp": meta.get("created"),
        "n_classes": len(LABEL_ENCODER.classes_),
        "n_features": len(FEATURE_NAMES),
        "classes": list(LABEL_ENCODER.classes_),
        "params": meta.get("params", {}),
    }


@app.post("/api/predict")
async def api_predict(
    body: PredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.symptoms:
        raise HTTPException(status_code=400, detail="symptoms must be a non-empty list")

    user_context = get_patient_context(current_user.id, db)
    result = predict_disease(body.symptoms, MODEL, LABEL_ENCODER, FEATURE_NAMES, disease_info)
    result["user_context"] = user_context
    return personalize_disease_prediction(result, user_context)


@app.get("/api/disease-info")
async def api_disease_info():
    return disease_info


@app.get("/api/disease-info/{disease}")
async def api_disease_info_specific(disease: str):
    result = {}
    if disease in disease_info['descriptions']:
        result['description'] = disease_info['descriptions'][disease]
    if disease in disease_info['precautions']:
        result['precautions'] = disease_info['precautions'][disease]
    if not result:
        raise HTTPException(status_code=404, detail=f'Disease "{disease}" not found')
    result['disease'] = disease
    return result

# ========================== AI CONSULTATION =================================

@app.post("/api/ai/image-analysis")
async def api_ai_image_analysis(
    image: UploadFile = File(...),
    query: str = Form(
        "You are a professional doctor. What's in this image? Do you find anything wrong with it medically? "
        "If you make a differential, suggest some remedies. Your response should be in one paragraph. "
        "Answer as if you are answering to a real person. Don't say 'In the image I see' but say "
        "'With what I see, I think you have....' Keep your answer concise (max 2 sentences). "
        "No preamble, start your answer right away."
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_context = get_patient_context(current_user.id, db)
    query_with_context = f"{query}\n\n{format_patient_context_for_prompt(user_context)}"
    image_bytes = await image.read()
    encoded_image = encode_image_from_bytes(image_bytes)
    analysis = analyze_image_with_groq(query_with_context, encoded_image)
    personalization = personalize_consultation_output(analysis, user_context)
    return {
        "analysis": analysis,
        "query": query,
        "filename": image.filename,
        "user_context": user_context,
        "personalized_insight_label": personalization["personalized_insight_label"],
        "personalized_insights": personalization["personalized_insights"],
        "personalized_warnings": personalization["personalized_warnings"],
        "personalized_recommendations": personalization["personalized_recommendations"],
    }


@app.post("/api/ai/transcribe")
async def api_ai_transcribe(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    transcription = transcribe_audio_with_groq(audio_bytes)
    return {"transcription": transcription, "filename": audio.filename}


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


@app.post("/api/ai/text-to-speech")
async def api_ai_text_to_speech(body: TTSRequest):
    if not body.text:
        raise HTTPException(status_code=400, detail="No text provided")
    audio_bytes = text_to_speech_gtts(body.text, body.language)
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio": audio_base64, "text": body.text, "language": body.language}
    raise HTTPException(status_code=500, detail="Failed to generate speech")


@app.post("/api/ai/full-consultation")
async def api_ai_full_consultation(
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_context = get_patient_context(current_user.id, db)
    transcription = ""
    if audio:
        audio_bytes = await audio.read()
        transcription = transcribe_audio_with_groq(audio_bytes)

    image_analysis = ""
    if image:
        image_bytes = await image.read()
        encoded_image = encode_image_from_bytes(image_bytes)
        query = (
            f"You are a professional doctor. {transcription} What's in this image? "
            "Do you find anything wrong with it medically? If you make a differential, suggest some remedies. "
            "Your response should be in one paragraph. Answer as if you are answering to a real person. "
            "Don't say 'In the image I see' but say 'With what I see, I think you have....' "
            "Keep your answer concise (max 2 sentences). No preamble, start your answer right away."
        )
        query = f"{query}\n\n{format_patient_context_for_prompt(user_context)}"
        image_analysis = analyze_image_with_groq(query, encoded_image)
    elif transcription.strip():
        text_query = (
            "You are a professional doctor assistant. "
            f"Patient says: {transcription}\n\n"
            f"{format_patient_context_for_prompt(user_context)}\n\n"
            "Respond with practical, safe, concise guidance in max 3 sentences, "
            "include any relevant cautions from allergies/conditions/medications, "
            "and advise doctor consultation for diagnosis."
        )
        image_analysis = consult_text_with_groq(text_query)

    response_text = image_analysis if image_analysis else "I need more information to provide a medical consultation."
    audio_bytes = text_to_speech_gtts(response_text)
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None

    consultation_personalization = personalize_consultation_output(response_text, user_context)

    return {
        "transcription": transcription,
        "analysis": image_analysis,
        "response_text": response_text,
        "response_audio": audio_base64,
        "user_context": user_context,
        "personalized_insight_label": consultation_personalization["personalized_insight_label"],
        "personalized_insights": consultation_personalization["personalized_insights"],
        "personalized_warnings": consultation_personalization["personalized_warnings"],
        "personalized_recommendations": consultation_personalization["personalized_recommendations"],
    }

# ========================== PRESCRIPTION ANALYSIS ===========================

@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze_prescription(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_file_extension(file.filename or ""):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a JPG, PNG, or PDF file.",
        )

    file_bytes = await file.read()

    if not validate_file_size(len(file_bytes)):
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: GROQ_API_KEY is not configured.",
        )

    try:
        user_context = get_patient_context(current_user.id, db)

        logger.info("Extracting text from prescription: %s", file.filename)
        raw_text = await extract_text_from_prescription(
            file_bytes, file.content_type or "image/jpeg"
        )

        logger.info("Extracting medicine names from text")
        medicines_raw = await extract_medicine_names(raw_text, user_context=user_context)

        if not medicines_raw:
            raise HTTPException(
                status_code=422,
                detail="No medicines could be detected in the uploaded prescription.",
            )

        results = []
        extracted_names: List[str] = []
        for med in medicines_raw:
            medicine_name = med.get("generic_name") or med.get("brand_name", "")
            if not medicine_name:
                continue
            extracted_names.append(medicine_name)
            logger.info("Getting alternatives for: %s", medicine_name)
            alternatives = await get_alternative_medicines(medicine_name)
            results.append(
                MedicineResult(
                    brand_name=med.get("brand_name", medicine_name),
                    generic_name=med.get("generic_name", medicine_name),
                    alternatives=alternatives,
                )
            )

        prescription_personalization = build_prescription_personalization(extracted_names, user_context)
        _merge_extracted_medications(db, current_user.id, extracted_names)

        return AnalysisResponse(
            medicines=results,
            raw_text=raw_text,
            disclaimer=DISCLAIMER,
            patient_context=user_context,
            safety_warnings=prescription_personalization["warnings"],
            personalized_recommendations=prescription_personalization["recommendations"],
            personalized_insights=prescription_personalization["insights"],
            personalized_insight_label="Personalized Insight",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during prescription analysis")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc

# ========================== HEALTH REPORT ANALYSIS ==========================

@app.post("/api/analyze-health-report")
async def analyze_health_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept a PDF or image lab report, extract text via vision model,
    then return a structured plain-English analysis via LLM.
    """
    if not validate_file_extension(file.filename or ""):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a JPG, PNG, or PDF file.",
        )

    file_bytes = await file.read()

    if not validate_file_size(len(file_bytes)):
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: GROQ_API_KEY is not configured.",
        )

    try:
        user_context = get_patient_context(current_user.id, db)

        logger.info("Extracting text from health report: %s", file.filename)
        raw_text = await extract_report_text(file_bytes, file.content_type or "image/jpeg")

        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from the uploaded report. Please ensure the file is a clear lab report.",
            )

        logger.info("Analyzing health report with LLM")
        analysis = await analyze_report_with_llm(raw_text, user_context=user_context)
        personalized_analysis = personalize_health_report_analysis(analysis, user_context)

        return {
            "analysis": personalized_analysis,
            "raw_text": raw_text,
            "user_context": user_context,
            "personalized_insight_label": "Personalized Insight",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during health report analysis")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc
