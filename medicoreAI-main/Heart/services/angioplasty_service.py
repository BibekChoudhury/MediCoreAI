"""
Heart Health Module - Angioplasty Report Analysis Service
NLP-based extraction of stent details, artery locations, and procedure outcomes
"""
import re
from typing import Dict, List
from sqlalchemy.orm import Session
from models.db_models import AngioplastyReport


# ── Medical Entity Patterns ───────────────────────────

ARTERY_PATTERNS = {
    "LAD": [r"\bLAD\b", r"left anterior descending", r"anterior descending"],
    "LCx": [r"\bLCx\b", r"\bLCX\b", r"left circumflex", r"circumflex artery"],
    "RCA": [r"\bRCA\b", r"right coronary artery", r"right coronary"],
    "LM": [r"\bLM\b", r"\bLMCA\b", r"left main", r"left main coronary"],
    "Diagonal": [r"\bD1\b", r"\bD2\b", r"diagonal branch", r"diagonal artery"],
    "OM": [r"\bOM\b", r"\bOM1\b", r"\bOM2\b", r"obtuse marginal"],
    "PDA": [r"\bPDA\b", r"posterior descending"],
    "PLV": [r"\bPLV\b", r"posterolateral"],
}

STENT_TYPES = {
    "drug_eluting": [r"drug.?eluting", r"\bDES\b", r"everolimus", r"zotarolimus",
                     r"sirolimus", r"paclitaxel", r"xience", r"resolute", r"synergy"],
    "bare_metal": [r"bare.?metal", r"\bBMS\b", r"metallic stent"],
    "bioresorbable": [r"bioresorbable", r"bioabsorbable", r"absorb"],
}

COMPLICATION_KEYWORDS = [
    "dissection", "perforation", "no-reflow", "slow flow", "thrombus",
    "hematoma", "bleeding", "arrhythmia", "hypotension", "bradycardia",
    "cardiac arrest", "ventricular fibrillation", "embolization",
    "contrast reaction", "vascular complication", "pseudoaneurysm"
]

SUCCESS_KEYWORDS = [
    "successful", "good result", "timi 3", "timi iii", "optimal result",
    "no complications", "uneventful", "residual stenosis 0%", "patent",
    "excellent flow", "good angiographic result"
]

STENOSIS_PATTERN = re.compile(r"(\d+)\s*%\s*(?:stenosis|narrowing|occlusion|block)")
STENT_SIZE_PATTERN = re.compile(r"(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)\s*mm")


def analyze_angioplasty_report(text: str) -> Dict:
    """Analyze angioplasty procedure report and extract structured information."""
    text_lower = text.lower()

    # Extract artery locations
    arteries = _extract_arteries(text)

    # Extract stent details
    stents = _extract_stent_details(text)

    # Detect complications
    complications = _detect_complications(text_lower)

    # Check procedure success
    success = _check_success(text_lower)

    # Extract stenosis percentages
    stenosis_values = STENOSIS_PATTERN.findall(text_lower)

    # Generate structured summary
    summary = _generate_summary(arteries, stents, complications, success, stenosis_values)

    # Generate patient-friendly explanation
    explanation = _generate_explanation(arteries, stents, complications, success)

    # Generate follow-up instructions
    follow_up = _generate_follow_up(stents, complications)

    return {
        "structured_summary": summary,
        "stent_details": stents,
        "artery_locations": arteries,
        "complications": ", ".join(complications) if complications else "No complications reported",
        "procedure_success": success,
        "stenosis_percentages": stenosis_values,
        "explanation": explanation,
        "follow_up_instructions": follow_up,
    }


def save_angioplasty_report(db: Session, user_id: int, analysis: Dict,
                            report_text: str) -> AngioplastyReport:
    """Save analysis results to database."""
    report = AngioplastyReport(
        user_id=user_id,
        report_text=report_text,
        extracted_findings=analysis,
        stent_details=analysis["stent_details"],
        artery_locations=analysis["artery_locations"],
        complications=analysis["complications"],
        explanation=analysis["explanation"],
        follow_up_instructions=analysis["follow_up_instructions"],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _extract_arteries(text: str) -> List[str]:
    found = []
    for artery, patterns in ARTERY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if artery not in found:
                    found.append(artery)
                break
    return found


def _extract_stent_details(text: str) -> List[Dict]:
    stents = []
    text_lower = text.lower()

    # Detect stent type
    stent_type = "Unknown"
    for stype, patterns in STENT_TYPES.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                stent_type = stype.replace("_", " ").title()
                break

    # Find stent dimensions
    sizes = STENT_SIZE_PATTERN.findall(text)

    # Find number of stents
    num_stents_match = re.search(r"(\d+)\s*(?:stent|stents)", text_lower)
    num_stents = int(num_stents_match.group(1)) if num_stents_match else max(1, len(sizes))

    for i in range(num_stents):
        stent = {
            "number": i + 1,
            "type": stent_type,
        }
        if i < len(sizes):
            stent["diameter_mm"] = float(sizes[i][0])
            stent["length_mm"] = float(sizes[i][1])
        stents.append(stent)

    return stents


def _detect_complications(text_lower: str) -> List[str]:
    found = []
    for keyword in COMPLICATION_KEYWORDS:
        if keyword in text_lower:
            # Check it's not "no complication"
            pattern = rf"(?:no|without|absent|none)\s+(?:\w+\s+)*{re.escape(keyword)}"
            if not re.search(pattern, text_lower):
                found.append(keyword.title())
    return found


def _check_success(text_lower: str) -> bool:
    return any(kw in text_lower for kw in SUCCESS_KEYWORDS)


def _generate_summary(arteries, stents, complications, success, stenosis) -> str:
    parts = []

    if stents:
        parts.append(f"{len(stents)} stent(s) placed")
        types = set(s.get("type", "Unknown") for s in stents)
        parts.append(f"({', '.join(types)})")

    if arteries:
        parts.append(f"in {', '.join(arteries)}")

    if success:
        parts.append("— procedure successful")

    if complications:
        parts.append(f"⚠️ Complications: {', '.join(complications)}")
    else:
        parts.append("— no complications")

    if stenosis:
        parts.append(f"| Pre-procedure stenosis: {', '.join(s + '%' for s in stenosis)}")

    return " ".join(parts) if parts else "Report analysis complete — limited structured data extracted."


def _generate_explanation(arteries, stents, complications, success) -> str:
    explain = []

    # Artery map for friendly names
    artery_names = {
        "LAD": "the main artery on the front of your heart (Left Anterior Descending)",
        "LCx": "the artery on the left side of your heart (Left Circumflex)",
        "RCA": "the artery on the right side of your heart (Right Coronary Artery)",
        "LM": "the main trunk artery (Left Main) — a critical vessel",
        "Diagonal": "a branch artery on the front of your heart",
        "OM": "a branch artery on the side of your heart",
        "PDA": "an artery on the back of your heart",
    }

    if arteries:
        artery_desc = [artery_names.get(a, a) for a in arteries]
        explain.append(f"The procedure was performed on {', '.join(artery_desc)}.") #type:ignore

    if stents:
        n = len(stents)
        stent_type = stents[0].get("type", "A")
        explain.append(
            f"{'A' if n == 1 else str(n)} {stent_type.lower()} stent{'s were' if n > 1 else ' was'} "
            f"placed to keep the artery open and restore blood flow."
        )
        if "Drug Eluting" in stent_type:
            explain.append(
                "Drug-eluting stents are coated with medication that slowly releases over time "
                "to prevent the artery from narrowing again."
            )

    if success:
        explain.append("Your doctor reported the procedure went well with good blood flow restored.")

    if complications:
        explain.append(
            f"However, the following complication(s) were noted: {', '.join(complications).lower()}. "
            "Your doctor will monitor these closely."
        )

    return " ".join(explain) if explain else "The report has been processed. Please consult your cardiologist for a detailed discussion of your results."


def _generate_follow_up(stents, complications) -> str:
    instructions = [
        "Continue antiplatelet medication as prescribed (typically dual antiplatelet therapy for 6-12 months)",
        "Attend all scheduled follow-up appointments",
        "Report any chest pain, shortness of breath, or unusual symptoms immediately",
    ]

    if any(s.get("type") == "Drug Eluting" for s in stents):
        instructions.append(
            "Do NOT stop dual antiplatelet therapy (aspirin + clopidogrel/prasugrel/ticagrelor) "
            "without consulting your cardiologist — this is critical to prevent stent thrombosis"
        )

    if complications:
        instructions.append("Additional monitoring may be required due to procedural complications")

    instructions.extend([
        "Adopt a heart-healthy diet low in saturated fats and sodium",
        "Begin cardiac rehabilitation exercise program as directed",
        "Manage risk factors: blood pressure, cholesterol, blood sugar",
    ])

    return " | ".join(instructions)
