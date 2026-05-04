import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
PRESCRIPTION_UPLOAD_ROOT = UPLOAD_ROOT / "prescriptions"


def ensure_upload_directories() -> None:
    PRESCRIPTION_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(filename: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", filename).strip("._")
    return safe or "file"


def save_prescription_file(user_id: int, upload_file: UploadFile, file_bytes: bytes) -> dict[str, str]:
    user_dir = PRESCRIPTION_UPLOAD_ROOT / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    sanitized = _sanitize_filename(upload_file.filename or "prescription")
    stored_name = f"{uuid.uuid4().hex}_{sanitized}"
    stored_path = user_dir / stored_name
    stored_path.write_bytes(file_bytes)

    relative_url = f"/uploads/prescriptions/{user_id}/{stored_name}"
    uploaded_at = datetime.now(timezone.utc).isoformat()
    return {
        "id": uuid.uuid4().hex,
        "file_name": upload_file.filename or sanitized,
        "file_url": relative_url,
        "stored_path": str(stored_path),
        "uploaded_at": uploaded_at,
    }
