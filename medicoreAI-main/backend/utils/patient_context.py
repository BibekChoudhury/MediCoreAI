from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from database import SessionLocal
from models.patient_profile import PatientProfile
from models.user import User


def _normalize_text_list(values: list[Any] | None) -> list[str]:
    if not values:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        value = str(item).strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(value)
    return normalized


def get_or_create_patient_profile(db: Session, user_id: int) -> PatientProfile:
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    if profile:
        return profile
    profile = PatientProfile(user_id=user_id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _build_context_payload(user: User, profile: PatientProfile) -> dict[str, Any]:
    return {
        "age": user.age,
        "blood_group": user.blood_group,
        "weight": profile.weight,
        "gender": profile.gender,
        "allergies": _normalize_text_list(profile.allergies),
        "conditions": _normalize_text_list(profile.conditions),
        "medications": _normalize_text_list(profile.medications),
    }


def get_patient_context(user_id: int, db: Session | None = None) -> dict[str, Any]:
    """
    Central reusable patient-context function.
    If no DB session is passed, this function creates one safely.
    """
    owns_session = db is None
    session = db or SessionLocal()
    try:
        user = session.get(User, user_id)
        if not user:
            return {
                "age": None,
                "blood_group": None,
                "weight": None,
                "gender": None,
                "allergies": [],
                "conditions": [],
                "medications": [],
            }
        profile = get_or_create_patient_profile(session, user_id)
        return _build_context_payload(user, profile)
    finally:
        if owns_session:
            session.close()


def format_patient_context_for_prompt(context: dict[str, Any] | None) -> str:
    if not context:
        return "Patient profile context is not available."
    return (
        "Patient profile context:\n"
        f"- Age: {context.get('age') if context.get('age') is not None else 'Unknown'}\n"
        f"- Blood group: {context.get('blood_group') or 'Unknown'}\n"
        f"- Weight: {context.get('weight') if context.get('weight') is not None else 'Unknown'}\n"
        f"- Gender: {context.get('gender') or 'Unknown'}\n"
        f"- Known allergies: {', '.join(context.get('allergies', [])) or 'None provided'}\n"
        f"- Existing conditions: {', '.join(context.get('conditions', [])) or 'None provided'}\n"
        f"- Current medications: {', '.join(context.get('medications', [])) or 'None provided'}\n"
        "Use this context to personalize output and avoid unsafe suggestions."
    )


def calculate_profile_completeness(user: User, profile: PatientProfile) -> tuple[int, list[str]]:
    fields = {
        "Age": bool(user.age),
        "Blood Group": bool(user.blood_group),
        "Weight": profile.weight is not None,
        "Gender": bool(profile.gender),
        "Allergies": bool(profile.allergies),
        "Existing Conditions": bool(profile.conditions),
        "Current Medications": bool(profile.medications),
    }
    completed = sum(1 for present in fields.values() if present)
    completeness = int((completed / len(fields)) * 100)
    missing_critical = [name for name, present in fields.items() if not present]
    return completeness, missing_critical


def build_missing_context_warnings(context: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if context.get("age") is None:
        warnings.append("Age is missing, so age-specific interpretation may be limited.")
    if not context.get("conditions"):
        warnings.append("Existing conditions are not set; risk personalization may be incomplete.")
    if not context.get("allergies"):
        warnings.append("Known allergies are not set; medication safety checks are limited.")
    return warnings
