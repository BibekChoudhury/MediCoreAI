import re
import logging

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "This tool provides informational alternatives only and is not a substitute "
    "for professional medical advice. Always consult a qualified healthcare "
    "professional before making changes to your medication."
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_file_extension(filename: str) -> bool:
    """Return True if the file extension is supported."""
    if not filename:
        return False
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(size_bytes: int) -> bool:
    """Return True if the file size is within the allowed limit."""
    return size_bytes <= MAX_FILE_SIZE_BYTES


def clean_json_response(text: str) -> str:
    """Strip markdown code fences from a JSON response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
