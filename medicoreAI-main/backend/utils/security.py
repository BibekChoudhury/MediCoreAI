import os
import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import HTTPException, status

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "replace-this-secret-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REMEMBER_ME_EXPIRE_DAYS = int(os.getenv("REMEMBER_ME_EXPIRE_DAYS", "30"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))


def _normalize_password_for_bcrypt(password: str) -> bytes:
    """
    Bcrypt accepts only the first 72 bytes of input.
    We pre-hash using SHA-256 hex so input length is fixed and safe.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


def hash_password(password: str) -> str:
    normalized = _normalize_password_for_bcrypt(password)
    return bcrypt.hashpw(normalized, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized = _normalize_password_for_bcrypt(plain_password)
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        if bcrypt.checkpw(normalized, hashed_bytes):
            return True
        # Backward compatibility: allow legacy raw bcrypt hashes.
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_bytes)
    except ValueError:
        return False


def validate_password_strength(password: str) -> None:
    checks = [
        (len(password) >= 8, "Password must be at least 8 characters long."),
        (re.search(r"[A-Z]", password), "Password must include at least one uppercase letter."),
        (re.search(r"[a-z]", password), "Password must include at least one lowercase letter."),
        (re.search(r"\d", password), "Password must include at least one number."),
        (
            re.search(r"[!@#$%^&*()_\-+={[}\]|\\:;\"'<,>.?/`~]", password),
            "Password must include at least one special character.",
        ),
    ]
    for is_valid, message in checks:
        if not is_valid:
            raise ValueError(message)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None, expires_delta: timedelta | None = None) -> tuple[str, int]:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    return token, expires_in


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc


def get_login_expiry(remember_me: bool) -> timedelta:
    if remember_me:
        return timedelta(days=REMEMBER_ME_EXPIRE_DAYS)
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
