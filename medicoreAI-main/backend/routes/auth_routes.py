from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from controllers.auth_controller import login_user, register_user
from database import get_db
from models.auth_schemas import LoginRequest, MessageResponse, RegisterRequest, TokenResponse, UserResponse

auth_router = APIRouter(tags=["Authentication"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(payload, db)


@auth_router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return login_user(payload, db)


@auth_router.post("/logout", response_model=MessageResponse)
def logout():
    return MessageResponse(message="Logged out. Please remove the token client-side.")
