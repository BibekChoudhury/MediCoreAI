from __future__ import annotations

from typing import Any


RESPIRATORY_TERMS = ("respiratory", "asthma", "bronchitis", "pneumonia", "copd")
DIABETES_RELATED_TERMS = ("glucose", "diabetes", "kidney", "neuropathy", "infection")
CARDIAC_TERMS = ("heart", "cardiac", "hypertension", "stroke")
FEMALE_SPECIFIC_TERMS = ("ovarian", "breast", "cervical", "pcos", "uterine")
MALE_SPECIFIC_TERMS = ("prostate", "testicular")

PENICILLIN_FAMILY = ("penicillin", "amoxicillin", "ampicillin", "augmentin", "flucloxacillin")
SULFA_FAMILY = ("sulfa", "sulfamethoxazole", "co-trimoxazole")
NSAID_FAMILY = ("ibuprofen", "diclofenac", "naproxen", "ketorolac")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def _safe_context(context: dict[str, Any] | None) -> dict[str, Any]:
    return context or {
        "age": None,
        "blood_group": None,
        "weight": None,
        "gender": None,
        "allergies": [],
        "conditions": [],
        "medications": [],
    }


def personalize_disease_prediction(result: dict[str, Any], context: dict[str, Any] | None) -> dict[str, Any]:
    ctx = _safe_context(context)
    conditions = [item.lower() for item in ctx.get("conditions", [])]
    gender = str(ctx.get("gender") or "").lower()
    age = ctx.get("age")

    top_predictions = result.get("top_predictions") or []
    if not top_predictions:
        result["personalized_insights"] = []
        result["personalized_recommendations"] = []
        result["personalized_warnings"] = []
        result["personalized_insight_label"] = "Personalized Insight"
        return result

    personalized_rows = []
    for row in top_predictions:
        score = float(row.get("probability", 0))
        disease = row.get("disease", "")
        disease_lower = disease.lower()
        reasons: list[str] = []

        if "asthma" in conditions and _contains_any(disease_lower, RESPIRATORY_TERMS):
            score *= 1.15
            reasons.append("Respiratory risk increased due to asthma history.")
        if "diabetes" in conditions and _contains_any(disease_lower, DIABETES_RELATED_TERMS):
            score *= 1.12
            reasons.append("Diabetes context raises relevance for metabolic/infection patterns.")
        if "hypertension" in conditions and _contains_any(disease_lower, CARDIAC_TERMS):
            score *= 1.10
            reasons.append("Hypertension history raises relevance for cardiovascular patterns.")
        if isinstance(age, int) and age >= 60 and _contains_any(disease_lower, CARDIAC_TERMS + DIABETES_RELATED_TERMS):
            score *= 1.08
            reasons.append("Age-related risk factor applied.")
        if gender == "female" and _contains_any(disease_lower, FEMALE_SPECIFIC_TERMS):
            score *= 1.18
            reasons.append("Female-specific condition weighting applied.")
        if gender == "male" and _contains_any(disease_lower, MALE_SPECIFIC_TERMS):
            score *= 1.18
            reasons.append("Male-specific condition weighting applied.")

        personalized_rows.append(
            {
                **row,
                "personalized_probability": score,
                "personalization_reasons": reasons,
            }
        )

    personalized_rows.sort(key=lambda item: item["personalized_probability"], reverse=True)
    total = sum(row["personalized_probability"] for row in personalized_rows) or 1.0
    for row in personalized_rows:
        row["personalized_probability"] = round(row["personalized_probability"] / total, 4)

    result["personalized_top_predictions"] = personalized_rows
    result["personalized_prediction"] = personalized_rows[0]["disease"]
    result["personalized_insight_label"] = "Personalized Insight"

    insights = []
    for row in personalized_rows[:3]:
        if row["personalization_reasons"]:
            insights.append(f"{row['disease']}: {' '.join(row['personalization_reasons'])}")
    result["personalized_insights"] = insights
    result["personalized_recommendations"] = [
        "These results were adjusted using your profile context.",
        "Seek clinical confirmation for diagnosis and treatment decisions.",
    ]
    result["personalized_warnings"] = []
    return result


def personalize_consultation_output(response_text: str, context: dict[str, Any] | None) -> dict[str, Any]:
    ctx = _safe_context(context)
    allergies = [item.lower() for item in ctx.get("allergies", [])]
    conditions = [item.lower() for item in ctx.get("conditions", [])]
    meds = [item.lower() for item in ctx.get("medications", [])]

    warnings: list[str] = []
    recommendations: list[str] = []
    insights: list[str] = []

    if allergies:
        warnings.append("Medication advice should be checked against your listed allergies.")
        insights.append(f"Allergy context applied: {', '.join(ctx.get('allergies', []))}.")
    if conditions:
        insights.append(f"Condition context applied: {', '.join(ctx.get('conditions', []))}.")
    if meds:
        warnings.append("Avoid adding medicines without checking interactions with your current medications.")
        insights.append(f"Current medication context applied: {', '.join(ctx.get('medications', []))}.")

    if "diabetes" in conditions:
        recommendations.append("Monitor glucose-related symptoms carefully and report persistent changes.")
    if "asthma" in conditions:
        recommendations.append("Track breathing patterns and seek urgent care for worsening shortness of breath.")
    if "hypertension" in conditions:
        recommendations.append("Monitor blood pressure regularly when symptoms are ongoing.")

    if not recommendations:
        recommendations.append("Follow up with a licensed doctor for personalized diagnosis.")

    return {
        "personalized_insight_label": "Personalized Insight",
        "personalized_insights": insights,
        "personalized_warnings": warnings,
        "personalized_recommendations": recommendations,
        "response_text": response_text,
    }


def build_prescription_personalization(medicine_names: list[str], context: dict[str, Any] | None) -> dict[str, list[str]]:
    ctx = _safe_context(context)
    allergies = [item.lower() for item in ctx.get("allergies", [])]
    conditions = [item.lower() for item in ctx.get("conditions", [])]
    current_meds = [item.lower() for item in ctx.get("medications", [])]

    warnings: list[str] = []
    recommendations: list[str] = []
    insights: list[str] = []

    for medicine in medicine_names:
        med = medicine.lower()

        if med in current_meds:
            warnings.append(f"{medicine} is already in your current medication list.")

        if ("penicillin" in allergies or "beta-lactam" in allergies) and _contains_any(med, PENICILLIN_FAMILY):
            warnings.append(f"{medicine} may conflict with your penicillin-related allergy history.")
            recommendations.append("Ask your doctor for a non-penicillin alternative.")
        if any("sulfa" in item for item in allergies) and _contains_any(med, SULFA_FAMILY):
            warnings.append(f"{medicine} may conflict with sulfa allergy history.")
            recommendations.append("Discuss sulfa-free alternatives with your clinician.")
        if "asthma" in conditions and _contains_any(med, NSAID_FAMILY):
            warnings.append(f"{medicine} can aggravate asthma in sensitive patients.")
        if "diabetes" in conditions and _contains_any(med, ("prednisone", "steroid")):
            warnings.append(f"{medicine} may increase blood glucose; monitor closely.")

    if allergies:
        insights.append(f"Allergy-aware medication checks applied ({', '.join(ctx.get('allergies', []))}).")
    if conditions:
        insights.append(f"Condition-aware checks applied ({', '.join(ctx.get('conditions', []))}).")

    if not recommendations:
        recommendations.append("Confirm medicine suitability with your prescribing doctor before changes.")

    return {
        "warnings": sorted(set(warnings)),
        "recommendations": sorted(set(recommendations)),
        "insights": insights,
    }


def personalize_health_report_analysis(analysis: dict[str, Any], context: dict[str, Any] | None) -> dict[str, Any]:
    ctx = _safe_context(context)
    conditions = [item.lower() for item in ctx.get("conditions", [])]
    age = ctx.get("age")

    profile_insights: list[str] = []
    profile_warnings: list[str] = []
    profile_recommendations: list[str] = []

    params = analysis.get("parameters", []) or []
    for param in params:
        name = str(param.get("name", "")).lower()
        status = str(param.get("status", "")).lower()

        if "diabetes" in conditions and any(token in name for token in ("glucose", "hba1c", "sugar")) and status in {"high", "low"}:
            profile_warnings.append("Glucose-related value is abnormal with existing diabetes history.")
            profile_recommendations.append("Discuss glucose control adjustments with your doctor soon.")
        if "hypertension" in conditions and any(token in name for token in ("cholesterol", "ldl", "triglyceride")) and status == "high":
            profile_warnings.append("Cardiovascular risk markers are elevated with hypertension history.")
            profile_recommendations.append("Prioritize cardiovascular risk follow-up and medication review.")
        if isinstance(age, int) and age >= 60 and any(token in name for token in ("creatinine", "egfr")) and status in {"high", "low"}:
            profile_warnings.append("Kidney function marker needs careful review in older age group.")
            profile_recommendations.append("Consider early nephrology consultation if advised by physician.")

    if ctx.get("conditions"):
        profile_insights.append(f"Interpretation personalized for conditions: {', '.join(ctx['conditions'])}.")
    if ctx.get("allergies"):
        profile_insights.append("Allergy context included for treatment-safety suggestions.")

    existing_recommendations = analysis.get("recommendations") or []
    merged_recommendations = existing_recommendations + [r for r in profile_recommendations if r not in existing_recommendations]
    analysis["recommendations"] = merged_recommendations
    analysis["personalized_insight_label"] = "Personalized Insight"
    analysis["personalized_insights"] = profile_insights
    analysis["profile_warnings"] = sorted(set(profile_warnings))
    analysis["profile_recommendations"] = sorted(set(profile_recommendations))
    return analysis
