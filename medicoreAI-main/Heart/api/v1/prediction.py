"""
Heart Health Module - Prediction Routes
Heart attack risk prediction endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import HeartPredictionInput, HeartPredictionResponse
from services.prediction_service import predict_heart_risk
from services.jarvis_personality import jarvis
from models.db_models import PredictionResult
from api.deps import get_current_user

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/heart-attack")
def api_predict_heart_attack(data: HeartPredictionInput, db: Session = Depends(get_db),
                              user=Depends(get_current_user)):
    """
    Predict heart attack risk with interpretable factors.
    Returns risk score, level, contributing factors, and JARVIS explanation.
    """
    input_dict = data.model_dump()
    result = predict_heart_risk(input_dict)

    # Save prediction if user is authenticated
    user_id = user.id if user else None
    if user_id:
        pred = PredictionResult(
            user_id=user_id,
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            contributing_factors=result["contributing_factors"],
            model_version=result["model_version"],
            input_data=input_dict,
        )
        db.add(pred)
        db.commit()

    # Add JARVIS-style narrative
    factors_text = ""
    if result["contributing_factors"]:
        top_factors = [f["factor"] for f in result["contributing_factors"][:3]]
        factors_text = f"Key factors include: {', '.join(top_factors)}."

    name = user.full_name if user else None
    result["jarvis_response"] = jarvis.prediction_response(
        name, result["risk_level"], result["risk_score"], factors_text
    )

    return result


@router.get("/history/{user_id}")
def api_prediction_history(user_id: int, limit: int = 10,
                           db: Session = Depends(get_db)):
    """Get prediction history for a user."""
    from sqlalchemy import desc
    predictions = db.query(PredictionResult).filter(
        PredictionResult.user_id == user_id
    ).order_by(desc(PredictionResult.timestamp)).limit(limit).all()

    return [{
        "id": p.id,
        "risk_score": p.risk_score,
        "risk_level": p.risk_level,
        "contributing_factors": p.contributing_factors,
        "timestamp": p.timestamp.isoformat() if p.timestamp else None,
    } for p in predictions]
