from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from controllers.profile_controller import (
    get_full_profile,
    update_full_profile,
    upload_prescriptions,
)
from database import get_db
from models.profile_schemas import (
    PrescriptionUploadResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from models.user import User
from utils.auth_dependencies import get_current_user

profile_router = APIRouter(tags=["Patient Profile"])


@profile_router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_full_profile(current_user, db)


@profile_router.put("/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_full_profile(current_user, payload, db)


@profile_router.post("/upload-prescriptions", response_model=PrescriptionUploadResponse)
async def upload_profile_prescriptions(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await upload_prescriptions(current_user, files, db)
