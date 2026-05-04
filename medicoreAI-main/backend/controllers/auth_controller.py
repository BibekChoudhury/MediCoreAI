from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.auth_schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from models.patient_profile import PatientProfile
from models.user import User
from utils.security import (
    create_access_token,
    get_login_expiry,
    hash_password,
    verify_password,
)


def register_user(payload: RegisterRequest, db: Session) -> UserResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        age=payload.age,
        blood_group=payload.blood_group.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = PatientProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    return UserResponse.model_validate(user)


def login_user(payload: LoginRequest, db: Session) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    expires_delta = get_login_expiry(payload.remember_me)
    token, expires_in = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )
