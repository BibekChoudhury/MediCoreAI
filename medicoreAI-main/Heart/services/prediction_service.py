"""
Heart Health Module - Prediction Service
Enhanced heart attack risk prediction with interpretable factors
"""
import os
import numpy as np
import joblib
import config

# Load trained model
_model = None


def _get_model():
    global _model
    if _model is None:
        model_path = config.ML_MODEL_PATH
        if os.path.exists(model_path):
            _model = joblib.load(model_path)
        else:
            # Fallback: check alternative path
            alt_path = os.path.join(config.BASE_DIR, "models", "ml", "heart_attack_model.pkl")
            if os.path.exists(alt_path):
                _model = joblib.load(alt_path)
            else:
                raise FileNotFoundError(f"Model not found at {model_path}")
    return _model


# Feature names and their clinical significance
FEATURE_NAMES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

FEATURE_LABELS = {
    "age": "Age",
    "sex": "Gender",
    "cp": "Chest Pain Type",
    "trestbps": "Resting Blood Pressure",
    "chol": "Cholesterol Level",
    "fbs": "Fasting Blood Sugar",
    "restecg": "Resting ECG",
    "thalach": "Max Heart Rate",
    "exang": "Exercise-Induced Angina",
    "oldpeak": "ST Depression",
    "slope": "ST Slope",
    "ca": "Major Vessels Colored",
    "thal": "Thalassemia"
}

# Normal ranges for risk assessment
NORMAL_RANGES = {
    "trestbps": (90, 120, "mmHg"),
    "chol": (125, 200, "mg/dl"),
    "thalach": (100, 180, "bpm"),
    "oldpeak": (0, 1.0, "mm"),
}

RISK_EXPLANATIONS = {
    "age": lambda v: f"Age {v} increases cardiovascular risk" if v > 55 else None,
    "sex": lambda v: "Male sex is associated with higher heart disease risk" if v == 1 else None,
    "cp": lambda v: {
        0: None,
        1: "Atypical chest pain present",
        2: "Non-anginal chest pain detected",
        3: "Asymptomatic presentation — can mask underlying disease"
    }.get(v),
    "trestbps": lambda v: f"Elevated resting blood pressure at {v} mmHg (normal < 120)" if v > 130 else (
        f"Low resting blood pressure at {v} mmHg" if v < 90 else None
    ),
    "chol": lambda v: f"High cholesterol at {v} mg/dl (recommended < 200)" if v > 240 else None,
    "fbs": lambda v: "Fasting blood sugar elevated (> 120 mg/dl) — diabetes indicator" if v == 1 else None,
    "restecg": lambda v: "Abnormal resting ECG findings" if v > 0 else None,
    "thalach": lambda v: f"Low maximum heart rate ({v} bpm) — may indicate reduced cardiac capacity" if v < 120 else None,
    "exang": lambda v: "Exercise-induced angina present — significant risk factor" if v == 1 else None,
    "oldpeak": lambda v: f"Significant ST depression ({v}mm) during exercise" if v > 1.5 else None,
    "slope": lambda v: "Downsloping ST segment — associated with higher risk" if v == 2 else None,
    "ca": lambda v: f"{v} major vessel(s) showing fluoroscopic narrowing" if v > 0 else None,
    "thal": lambda v: {
        0: None, 1: "Fixed thalassemia defect detected",
        2: None, 3: "Reversible thalassemia defect — indicates ischemia"
    }.get(v)
}


def predict_heart_risk(data: dict) -> dict:
    """
    Run heart attack prediction with interpretable risk factors.
    Returns risk score, level, contributing factors, summary, and tips.
    """
    try:
        model = _get_model()

        features = np.array([[data[f] for f in FEATURE_NAMES]])
        prob = float(model.predict_proba(features)[0][1])

        # Classify risk
        if prob < 0.2:
            level = "Low"
        elif prob < 0.5:
            level = "Moderate"
        elif prob < 0.8:
            level = "High"
        else:
            level = "Critical"

        # Extract contributing factors
        contributing_factors = []
        importances = {}
        if hasattr(model, "feature_importances_"):
            importances = dict(zip(FEATURE_NAMES, model.feature_importances_))

        for feature in FEATURE_NAMES:
            value = data[feature]
            explanation_fn = RISK_EXPLANATIONS.get(feature)
            explanation = explanation_fn(value) if explanation_fn else None

            if explanation:
                importance = importances.get(feature, 0.5)
                severity = "high" if importance > 0.1 else ("medium" if importance > 0.05 else "low")
                contributing_factors.append({
                    "factor": FEATURE_LABELS.get(feature, feature),
                    "value": value,
                    "severity": severity,
                    "explanation": explanation
                })

        # Sort by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        contributing_factors.sort(key=lambda x: severity_order.get(x["severity"], 3))

        # Generate summary
        n_factors = len(contributing_factors)
        if level == "Low":
            summary = "Your heart health indicators are mostly within normal ranges. Keep maintaining a healthy lifestyle."
        elif level == "Moderate":
            top_factors = ", ".join([f["factor"].lower() for f in contributing_factors[:2]])
            summary = f"Moderate risk detected with {n_factors} contributing factor(s). Key concerns: {top_factors}. Regular monitoring recommended."
        elif level == "High":
            top_factors = ", ".join([f["factor"].lower() for f in contributing_factors[:3]])
            summary = f"Elevated risk detected. {n_factors} risk factors identified including {top_factors}. Please consult your cardiologist."
        else:
            summary = f"Critical risk level with {n_factors} significant factors. Immediate medical consultation strongly recommended."

        # Generate tips
        tips = _generate_tips(level, contributing_factors, data)

        return {
            "risk_score": round(prob, 4),
            "risk_level": level,
            "contributing_factors": contributing_factors,
            "summary": summary,
            "tips": tips,
            "model_version": "v1.0"
        }

    except FileNotFoundError:
        return {
            "risk_score": 0.0,
            "risk_level": "Unknown",
            "contributing_factors": [],
            "summary": "Model not available. Please ensure the ML model is trained and placed in models/ml/.",
            "tips": ["Please contact system administrator to set up the prediction model."],
            "model_version": "v1.0"
        }
    except Exception as e:
        return {
            "risk_score": 0.0,
            "risk_level": "Error",
            "contributing_factors": [],
            "summary": f"Prediction error: {str(e)}",
            "tips": [],
            "model_version": "v1.0"
        }


def _generate_tips(level: str, factors: list, data: dict) -> list:
    tips = []

    if level in ("High", "Critical"):
        tips.append("⚠️ Consult a cardiologist as soon as possible")
        tips.append("Monitor blood pressure and heart rate daily")

    # Specific factor-based tips
    if data.get("chol", 0) > 200:
        tips.append("Reduce cholesterol: limit saturated fats, increase fiber intake")
    if data.get("trestbps", 0) > 130:
        tips.append("Lower blood pressure: reduce sodium, exercise regularly, manage stress")
    if data.get("fbs", 0) == 1:
        tips.append("Manage blood sugar: follow diabetes management plan, monitor glucose levels")
    if data.get("exang", 0) == 1:
        tips.append("If experiencing chest pain during exercise, stop immediately and rest")

    # General tips
    if level == "Moderate":
        tips.extend([
            "Exercise 30 minutes of moderate activity at least 5 days a week",
            "Maintain a heart-healthy Mediterranean-style diet",
            "Schedule regular cardiac check-ups every 6 months"
        ])
    elif level == "Low":
        tips.extend([
            "Continue your healthy lifestyle habits",
            "Annual heart health check-ups are recommended",
            "Stay active and maintain a balanced diet"
        ])

    return tips[:6]  # Limit to 6 tips
