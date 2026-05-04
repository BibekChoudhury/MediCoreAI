import logging
import base64
import os

from groq import Groq
from utils.file_processing import prepare_for_groq

logger = logging.getLogger(__name__)

OCR_PROMPT = (
    "Extract only the medicine names from the following prescription image. "
    "Ignore patient details, doctor information, and dosage instructions. "
    "If you find brand names, also include the generic name. "
    'Return the output as a JSON array of objects with "brand_name" and "generic_name" fields. '
    "Example: [{\"brand_name\": \"Crocin\", \"generic_name\": \"Paracetamol\"}]. "
    "If no medicines are found return an empty array []."
)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


async def extract_text_from_prescription(file_bytes: bytes, content_type: str) -> str:
    """
    Send the prescription image/PDF to Groq Vision and return the raw text response.
    """
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
                    {"type": "text", "text": OCR_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{encoded}",
                        },
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content
