import json
import logging
import os
from typing import List, Dict

from groq import Groq

from utils.helpers import clean_json_response

logger = logging.getLogger(__name__)

TEXT_MODEL = "llama-3.3-70b-versatile"

NORMALIZE_PROMPT = (
    "You are given raw OCR text from a medical prescription. "
    "Extract only the medicine names from this text. "
    "Ignore patient details, doctor information, clinic names, dates, and dosage instructions. "
    "Normalize any brand names to their generic equivalents where possible. "
    "Return the result as a JSON array of objects with 'brand_name' and 'generic_name' fields. "
    "If the text already contains a JSON array, validate and clean it instead. "
    "Patient profile context is provided below; use it for safety flags only, not for inventing medicines. "
    "Return only the JSON array, no other text.\n\nPrescription text:\n{text}"
)


def _profile_context_block(user_context: dict | None) -> str:
    if not user_context:
        return "No patient profile context provided."
    return (
        f"Allergies: {', '.join(user_context.get('allergies', [])) or 'None'}; "
        f"Conditions: {', '.join(user_context.get('conditions', [])) or 'None'}; "
        f"Current Medications: {', '.join(user_context.get('medications', [])) or 'None'}."
    )


async def extract_medicine_names(raw_text: str, user_context: dict | None = None) -> List[Dict[str, str]]:
    """
    Parse the raw OCR text / JSON response and return a list of
    {'brand_name': ..., 'generic_name': ...} dicts.
    """
    cleaned = clean_json_response(raw_text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return _normalize_list(data)
    except (json.JSONDecodeError, ValueError):
        pass

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"{NORMALIZE_PROMPT.format(text=raw_text)}\n\nPatient context:\n{_profile_context_block(user_context)}"
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    cleaned = clean_json_response(response.choices[0].message.content)

    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return _normalize_list(data)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Could not parse medicine names from Groq response: %s", response.choices[0].message.content)
        return []

    return []


def _normalize_list(data: list) -> List[Dict[str, str]]:
    """Ensure every item has brand_name and generic_name keys."""
    result = []
    for item in data:
        if not isinstance(item, dict):
            continue
        brand = str(item.get("brand_name") or item.get("name") or "").strip()
        generic = str(item.get("generic_name") or brand).strip()
        if brand or generic:
            result.append({"brand_name": brand, "generic_name": generic or brand})
    return result
