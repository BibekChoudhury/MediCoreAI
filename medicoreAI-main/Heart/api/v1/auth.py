"""
Heart Health Module - Auth Routes
Registration, login, and user management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from services.auth_service import register_user, authenticate_user, create_access_token
from api.deps import require_auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def api_register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    from models.db_models import User
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = register_user(
        db, data.username, data.email, data.password,
        full_name=data.full_name, age=data.age, gender=data.gender, role=data.role.value
    )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def api_login(data: UserLogin, db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def api_me(user=Depends(require_auth)):
    """Get current authenticated user info."""
    return UserResponse.model_validate(user)
