from fastapi import Request
from fastapi.responses import JSONResponse

from database import SessionLocal
from models.user import User
from utils.security import decode_access_token

PUBLIC_PATHS = {
    "/health",
    "/api/health",
    "/login",
    "/register",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/data/health/submit",        # Redirect to Heart sub-app (Android app)
    "/api/v1/data/callback/google-fit",  # Redirect to Heart sub-app (Google OAuth)
}

PUBLIC_PREFIXES = (
    "/heart/",       # Heart sub-app has its own auth
)

PROTECTED_PREFIXES = ("/api/",)
PROTECTED_PATHS = {"/profile", "/upload-prescriptions"}


async def jwt_auth_middleware(request: Request, call_next):
    path = request.url.path

    if request.method == "OPTIONS":
        return await call_next(request)

    if path in PUBLIC_PATHS:
        return await call_next(request)

    if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
        return await call_next(request)

    needs_auth = path in PROTECTED_PATHS or any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)
    if not needs_auth:
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing bearer token."},
        )

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token payload."},
            )

        db = SessionLocal()
        try:
            user = db.get(User, int(user_id))
        finally:
            db.close()

        if not user:
            return JSONResponse(
                status_code=401,
                content={"detail": "User associated with token no longer exists."},
            )

        request.state.current_user_id = user.id
        request.state.current_user_email = user.email
    except Exception as exc:
        detail = getattr(exc, "detail", "Invalid authentication token.")
        return JSONResponse(
            status_code=401,
            content={"detail": detail},
        )

    return await call_next(request)
