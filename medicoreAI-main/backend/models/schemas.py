from pydantic import BaseModel, Field
from typing import List, Optional


class AlternativeMedicine(BaseModel):
    name: str
    description: str


class AlternativesGroup(BaseModel):
    allopathy: List[AlternativeMedicine] = Field(default_factory=list)
    ayurveda: List[AlternativeMedicine] = Field(default_factory=list)
    homeopathy: List[AlternativeMedicine] = Field(default_factory=list)


class MedicineResult(BaseModel):
    brand_name: str
    generic_name: str
    alternatives: AlternativesGroup


class AnalysisResponse(BaseModel):
    medicines: List[MedicineResult]
    raw_text: str
    disclaimer: str
    patient_context: dict = Field(default_factory=dict)
    safety_warnings: List[str] = Field(default_factory=list)
    personalized_recommendations: List[str] = Field(default_factory=list)
    personalized_insights: List[str] = Field(default_factory=list)
    personalized_insight_label: str | None = None


class HealthResponse(BaseModel):
    status: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
