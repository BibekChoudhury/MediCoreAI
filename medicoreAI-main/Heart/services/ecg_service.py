"""
Heart Health Module - ECG Analysis Service
Analyzes ECG reports from images, PDFs, or text for cardiac abnormalities
"""
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from models.db_models import ECGReport


# ── ECG Pattern Definitions ────────────────────────────

ECG_PATTERNS = {
    "normal_sinus_rhythm": {
        "keywords": ["normal sinus", "nsr", "regular rhythm", "normal ecg", "within normal limits"],
        "label": "Normal Sinus Rhythm",
        "severity": "normal",
        "explanation": "Your heart is beating in a healthy, regular pattern. The electrical signals are following the normal pathway through your heart.",
        "recommendation": "No immediate action needed. Continue routine cardiac check-ups."
    },
    "atrial_fibrillation": {
        "keywords": ["atrial fibrillation", "afib", "a-fib", "a.fib", "irregularly irregular",
                     "fibrillation", "absent p waves", "no p waves"],
        "label": "Atrial Fibrillation",
        "severity": "moderate",
        "explanation": "Your ECG shows an irregular heartbeat pattern called atrial fibrillation. This means the upper chambers of your heart (atria) are beating out of sync with the lower chambers. It's one of the most common heart rhythm disorders.",
        "recommendation": "Consult your cardiologist for evaluation. May require anticoagulation therapy to reduce stroke risk."
    },
    "st_elevation": {
        "keywords": ["st elevation", "st segment elevation", "stemi", "st raised", "acute mi"],
        "label": "ST Elevation",
        "severity": "critical",
        "explanation": "Your ECG shows ST segment elevation, which can indicate that a portion of your heart muscle isn't receiving adequate blood flow. This is a serious finding that requires immediate medical attention.",
        "recommendation": "⚠️ URGENT: Seek immediate medical attention. ST elevation may indicate an acute heart attack."
    },
    "st_depression": {
        "keywords": ["st depression", "st segment depression", "st depressed"],
        "label": "ST Depression",
        "severity": "moderate",
        "explanation": "Your ECG shows ST segment depression, which may indicate reduced blood flow to part of your heart muscle. This can occur with coronary artery disease or after vigorous exercise.",
        "recommendation": "Consult your cardiologist. May require stress testing for further evaluation."
    },
    "bradycardia": {
        "keywords": ["bradycardia", "slow heart", "heart rate below 60", "hr < 60", "low rate"],
        "label": "Bradycardia",
        "severity": "mild",
        "explanation": "Your heart rate is slower than normal (below 60 beats per minute). This can be normal for athletes or during sleep, but may need evaluation if causing symptoms like dizziness or fatigue.",
        "recommendation": "If experiencing dizziness, fatigue, or fainting, consult your doctor."
    },
    "tachycardia": {
        "keywords": ["tachycardia", "fast heart", "rapid rate", "heart rate above 100", "hr > 100",
                     "sinus tachycardia"],
        "label": "Tachycardia",
        "severity": "mild",
        "explanation": "Your heart rate is faster than normal (above 100 beats per minute at rest). This can be caused by stress, caffeine, exercise, fever, or various medical conditions.",
        "recommendation": "If persistent at rest without obvious cause, consult your doctor."
    },
    "left_ventricular_hypertrophy": {
        "keywords": ["lvh", "left ventricular hypertrophy", "voltage criteria", "sokolow"],
        "label": "Left Ventricular Hypertrophy",
        "severity": "moderate",
        "explanation": "Your ECG shows signs of left ventricular hypertrophy — the main pumping chamber of your heart appears thickened. This is commonly associated with long-standing high blood pressure.",
        "recommendation": "Follow up with your cardiologist. Blood pressure management is essential."
    },
    "pvc": {
        "keywords": ["pvc", "premature ventricular", "ventricular ectopy", "ventricular premature"],
        "label": "Premature Ventricular Contractions",
        "severity": "mild",
        "explanation": "Your ECG shows premature ventricular contractions — extra heartbeats from the lower chambers. Occasional PVCs are common and usually harmless, but frequent PVCs should be evaluated.",
        "recommendation": "If rare, no action needed. If frequent (>10% of beats), consult your cardiologist."
    },
    "qt_prolongation": {
        "keywords": ["qt prolongation", "prolonged qt", "long qt", "qtc prolonged"],
        "label": "QT Prolongation",
        "severity": "moderate",
        "explanation": "Your ECG shows a prolonged QT interval, meaning your heart takes longer than normal to recharge between beats. This can increase the risk of dangerous heart rhythms.",
        "recommendation": "Review medications with your doctor, as some drugs can cause QT prolongation. Electrolyte levels should be checked."
    },
    "heart_block": {
        "keywords": ["heart block", "av block", "first degree block", "second degree", "third degree",
                     "complete block", "mobitz"],
        "label": "Heart Block",
        "severity": "moderate",
        "explanation": "Your ECG shows a conduction delay between the upper and lower chambers of your heart. The severity depends on the degree of block.",
        "recommendation": "Consult your cardiologist. Higher-degree blocks may require a pacemaker."
    }
}

SEVERITY_ORDER = {"normal": 0, "mild": 1, "moderate": 2, "critical": 3}


def analyze_ecg_text(text: str) -> Dict:
    """Analyze ECG report text and detect abnormalities."""
    text_lower = text.lower()
    findings = []
    risk_flags = []
    max_severity = "normal"

    for pattern_key, pattern_info in ECG_PATTERNS.items():
        for keyword in pattern_info["keywords"]:
            if keyword in text_lower:
                findings.append(pattern_info["label"])
                if pattern_info["severity"] != "normal":
                    risk_flags.append(pattern_info["label"])
                    if SEVERITY_ORDER.get(pattern_info["severity"], 0) > SEVERITY_ORDER.get(max_severity, 0):
                        max_severity = pattern_info["severity"]
                break  # Don't double-count same pattern

    # Remove duplicates
    findings = list(dict.fromkeys(findings))
    risk_flags = list(dict.fromkeys(risk_flags))

    # If no findings detected, assume could be normal or unreadable
    if not findings:
        findings = ["Unable to detect specific patterns — manual review recommended"]

    # Generate summary and explanation
    is_normal = max_severity == "normal" and not risk_flags
    summary = _generate_summary(findings, is_normal)
    explanation = _generate_explanation(findings, text_lower)
    recommendations = _generate_recommendations(findings, max_severity)

    return {
        "summary": summary,
        "detailed_explanation": explanation,
        "findings": findings,
        "recommendations": recommendations,
        "risk_flags": risk_flags,
        "severity": max_severity,
        "is_normal": is_normal,
    }


def save_ecg_report(db: Session, user_id: int, analysis: Dict,
                    file_url: Optional[str] = None, file_type: Optional[str] = None,
                    raw_text: Optional[str] = None) -> ECGReport:
    """Save ECG analysis results to database."""
    report = ECGReport(
        user_id=user_id,
        file_url=file_url,
        file_type=file_type,
        raw_text=raw_text,
        summary=analysis["summary"],
        detailed_explanation=analysis["detailed_explanation"],
        findings=analysis["findings"],
        recommendations=analysis["recommendations"],
        risk_flags=analysis["risk_flags"],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _generate_summary(findings: List[str], is_normal: bool) -> str:
    if is_normal:
        return "Normal sinus rhythm detected. No significant abnormalities found."
    n = len(findings)
    return f"{n} finding(s) detected: {', '.join(findings[:3])}{'...' if n > 3 else ''}."


def _generate_explanation(findings: List[str], text_lower: str) -> str:
    explanations = []
    for pattern_key, pattern_info in ECG_PATTERNS.items():
        if pattern_info["label"] in findings:
            explanations.append(f"**{pattern_info['label']}**: {pattern_info['explanation']}")

    if not explanations:
        return "The ECG data has been processed but specific pattern matching returned limited results. A manual review by a cardiologist is recommended for definitive interpretation."

    return "\n\n".join(explanations)


def _generate_recommendations(findings: List[str], max_severity: str) -> str:
    recs = []
    for pattern_key, pattern_info in ECG_PATTERNS.items():
        if pattern_info["label"] in findings and pattern_info.get("recommendation"):
            recs.append(pattern_info["recommendation"])

    if max_severity == "critical":
        recs.insert(0, "⚠️ CRITICAL FINDING: Seek immediate medical evaluation.")
    elif not recs:
        recs.append("Continue routine cardiac monitoring.")

    return " | ".join(recs)
