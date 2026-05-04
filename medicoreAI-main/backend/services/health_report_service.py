import os
import base64
import json
import logging
import re

from groq import Groq
from utils.file_processing import prepare_for_groq

logger = logging.getLogger(__name__)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
LLM_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a medical report interpreter for patients with no medical background. "
    "Your job is to read lab reports and explain them in simple, friendly language. "
    "Never diagnose. Always recommend consulting a doctor for abnormal values."
)

USER_PROMPT_TEMPLATE = """Here is the extracted text from a patient's lab report:

{extracted_text}

Patient profile context (if available):
{context_block}

Please return a JSON response with this exact structure:
{{
  "patient_info": {{ "name": "", "age": "", "date": "", "report_type": "" }},
  "summary": "A 2-3 sentence plain English overall summary of the report",
  "parameters": [
    {{
      "name": "Parameter name e.g. Hemoglobin",
      "value": "Patient value e.g. 11.2",
      "unit": "g/dL",
      "normal_range": "13.0 - 17.0",
      "status": "low",
      "plain_english": "Simple 1 line explanation e.g. Your hemoglobin is slightly low, which may cause tiredness"
    }}
  ],
  "flags": {{
    "critical": ["list of critical abnormal parameters if any"],
    "borderline": ["list of borderline parameters"]
  }},
  "recommendations": [
    "3-4 general lifestyle/dietary tips based on the findings. Always end with: consult your doctor for medical advice."
  ]
}}
Only return valid JSON, no extra text."""

EXTRACTION_PROMPT = (
    "Extract all text content from this lab report image exactly as it appears. "
    "Include all parameter names, values, units, reference ranges, patient information "
    "(name, age, date), report title, and any other visible text. "
    "Preserve the structure and layout as much as possible with plain text."
)


async def extract_report_text(file_bytes: bytes, content_type: str) -> str:
    """Use vision model to extract raw text from a lab report image or PDF."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Convert PDF→image and downscale oversized images before sending to Groq
    image_bytes, mime = prepare_for_groq(file_bytes, content_type)
    encoded = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{encoded}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content


def _build_context_block(user_context: dict | None) -> str:
    if not user_context:
        return "No additional patient profile context provided."

    return (
        f"Age: {user_context.get('age')}, "
        f"Blood Group: {user_context.get('blood_group')}, "
        f"Weight: {user_context.get('weight') or 'Unknown'}, "
        f"Gender: {user_context.get('gender') or 'Unknown'}, "
        f"Allergies: {', '.join(user_context.get('allergies', [])) or 'None'}, "
        f"Conditions: {', '.join(user_context.get('conditions', [])) or 'None'}, "
        f"Medications: {', '.join(user_context.get('medications', [])) or 'None'}."
    )


async def analyze_report_with_llm(extracted_text: str, user_context: dict | None = None) -> dict:
    """Send extracted text to LLM and return structured analysis as a dict."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(
                    extracted_text=extracted_text,
                    context_block=_build_context_block(user_context),
                ),
            },
        ],
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model wrapped the JSON
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    # Extract JSON object substring as a fallback
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if json_match:
        content = json_match.group()

    return json.loads(content)
