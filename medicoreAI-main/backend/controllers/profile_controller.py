from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from models.patient_profile import PatientProfile
from models.profile_schemas import (
    PrescriptionUploadResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from models.user import User
from services.medicine_service import extract_medicine_names
from services.ocr_service import extract_text_from_prescription
from utils.helpers import validate_file_extension, validate_file_size
from utils.patient_context import calculate_profile_completeness, get_or_create_patient_profile
from utils.storage import save_prescription_file


def _coerce_datetime(value: str | datetime | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)


def _normalize_prescription_entries(entries: list[dict] | None) -> list[dict]:
    if not entries:
        return []
    normalized = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        if not item.get("id") or not item.get("file_name") or not item.get("file_url"):
            continue
        normalized.append(
            {
                "id": str(item["id"]),
                "file_name": str(item["file_name"]),
                "file_url": str(item["file_url"]),
                "stored_path": str(item.get("stored_path", "")),
                "uploaded_at": _coerce_datetime(item.get("uploaded_at")).isoformat(),
            }
        )
    return normalized


def _sync_removed_files(existing_entries: list[dict], new_entries: list[dict]) -> None:
    remaining_ids = {entry.get("id") for entry in new_entries}
    for entry in existing_entries:
        entry_id = entry.get("id")
        stored_path = entry.get("stored_path")
        if entry_id in remaining_ids or not stored_path:
            continue
        path = Path(stored_path)
        if path.exists():
            path.unlink(missing_ok=True)


def _build_profile_response(user: User, profile: PatientProfile) -> ProfileResponse:
    completeness, missing_critical = calculate_profile_completeness(user, profile)
    return ProfileResponse(
        id=user.id,
        email=user.email,
        age=user.age,
        blood_group=user.blood_group,
        weight=profile.weight,
        gender=profile.gender,
        allergies=profile.allergies or [],
        conditions=profile.conditions or [],
        medications=profile.medications or [],
        prescription_files=[
            {
                **entry,
                "uploaded_at": _coerce_datetime(entry.get("uploaded_at")),
            }
            for entry in (profile.prescription_files or [])
        ],
        profile_completeness=completeness,
        missing_critical_fields=missing_critical,
        created_at=user.created_at,
        updated_at=profile.updated_at,
    )


def get_full_profile(current_user: User, db: Session) -> ProfileResponse:
    profile = get_or_create_patient_profile(db, current_user.id)
    return _build_profile_response(current_user, profile)


def update_full_profile(current_user: User, payload: ProfileUpdateRequest, db: Session) -> ProfileResponse:
    profile = get_or_create_patient_profile(db, current_user.id)
    fields_set = payload.model_fields_set

    if "age" in fields_set and payload.age is not None:
        current_user.age = payload.age
    if "blood_group" in fields_set and payload.blood_group is not None:
        current_user.blood_group = payload.blood_group.value

    if "weight" in fields_set:
        profile.weight = payload.weight
    if "gender" in fields_set:
        profile.gender = payload.gender.value if payload.gender else None
    if payload.allergies is not None:
        profile.allergies = payload.allergies
    if payload.conditions is not None:
        profile.conditions = payload.conditions
    if payload.medications is not None:
        profile.medications = payload.medications
    if payload.prescription_files is not None:
        new_entries = [entry.model_dump(mode="json") for entry in payload.prescription_files]
        existing_entries = profile.prescription_files or []
        _sync_removed_files(existing_entries, new_entries)
        profile.prescription_files = new_entries

    db.add(current_user)
    db.add(profile)
    db.commit()
    db.refresh(current_user)
    db.refresh(profile)
    return _build_profile_response(current_user, profile)


async def upload_prescriptions(
    current_user: User,
    files: list[UploadFile],
    db: Session,
) -> PrescriptionUploadResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload at least one prescription file.",
        )

    profile = get_or_create_patient_profile(db, current_user.id)
    uploaded_files = []
    extracted_medications: set[str] = set()

    for file in files:
        if not validate_file_extension(file.filename or ""):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format for {file.filename}. Upload JPG, PNG, or PDF.",
            )

        file_bytes = await file.read()
        if not validate_file_size(len(file_bytes)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} exceeds size limit.",
            )

        saved = save_prescription_file(current_user.id, file, file_bytes)
        uploaded_files.append(saved)

        try:
            raw_text = await extract_text_from_prescription(file_bytes, file.content_type or "image/jpeg")
            meds = await extract_medicine_names(raw_text)
            for med in meds:
                if med.get("generic_name"):
                    extracted_medications.add(med["generic_name"])
                elif med.get("brand_name"):
                    extracted_medications.add(med["brand_name"])
        except Exception:
            # OCR/LLM extraction is best effort; upload should still succeed.
            pass

    existing_entries = _normalize_prescription_entries(profile.prescription_files)
    merged_entries = existing_entries + uploaded_files
    profile.prescription_files = merged_entries

    if extracted_medications:
        current = {item.lower(): item for item in (profile.medications or [])}
        for med in sorted(extracted_medications):
            key = med.lower()
            if key not in current:
                current[key] = med
        profile.medications = list(current.values())

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return PrescriptionUploadResponse(
        uploaded_files=[
            {
                **entry,
                "uploaded_at": _coerce_datetime(entry.get("uploaded_at")),
            }
            for entry in uploaded_files
        ],
        extracted_medications=sorted(extracted_medications),
    )
