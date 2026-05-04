from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from models.patient_profile import Gender
from models.user import BloodGroup


class PrescriptionFile(BaseModel):
    id: str
    file_name: str
    file_url: str
    stored_path: str
    uploaded_at: datetime


class ProfileResponse(BaseModel):
    id: int
    email: EmailStr
    age: int
    blood_group: BloodGroup
    weight: float | None = None
    gender: Gender | None = None
    allergies: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    prescription_files: list[PrescriptionFile] = Field(default_factory=list)
    profile_completeness: int
    missing_critical_fields: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None


class ProfileUpdateRequest(BaseModel):
    age: int | None = Field(default=None, ge=1, le=120)
    blood_group: BloodGroup | None = None
    weight: float | None = Field(default=None, gt=0)
    gender: Gender | None = None
    allergies: list[str] | None = None
    conditions: list[str] | None = None
    medications: list[str] | None = None
    prescription_files: list[PrescriptionFile] | None = None

    @field_validator("allergies", "conditions", "medications")
    @classmethod
    def normalize_string_lists(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in values:
            value = str(item).strip()
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(value)
        return cleaned


class PrescriptionUploadResponse(BaseModel):
    uploaded_files: list[PrescriptionFile]
    extracted_medications: list[str] = Field(default_factory=list)


class UserContextResponse(BaseModel):
    age: int
    blood_group: BloodGroup
    weight: float | None = None
    allergies: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    gender: Gender | None = None

    @classmethod
    def from_raw(cls, data: dict[str, Any]) -> "UserContextResponse":
        return cls(**data)
