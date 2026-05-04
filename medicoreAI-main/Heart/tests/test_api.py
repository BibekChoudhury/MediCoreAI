"""
Heart Health Module - API Integration Tests
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force test database
os.environ["DATABASE_URL"] = "sqlite:///test_heart_health.db"

from models.database import init_db
from fastapi.testclient import TestClient
from main import app

# Ensure tables exist
init_db()

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "Heart Health Module v2"
    assert "endpoints" in data


def test_register_user():
    """Test user registration."""
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "age": 45,
        "gender": "male",
        "role": "patient"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "testuser"


def test_login():
    """Test user login."""
    # First register
    client.post("/api/v1/auth/register", json={
        "username": "logintest",
        "email": "login@example.com",
        "password": "testpass123",
    })
    # Then login
    response = client.post("/api/v1/auth/login", json={
        "username": "logintest",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_predict_heart_attack():
    """Test heart attack prediction endpoint."""
    response = client.post("/api/v1/predict/heart-attack", json={
        "age": 55,
        "sex": 1,
        "cp": 2,
        "trestbps": 130,
        "chol": 250,
        "fbs": 0,
        "restecg": 1,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 1.2,
        "slope": 2,
        "ca": 0,
        "thal": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert "contributing_factors" in data
    assert "summary" in data
    assert "tips" in data
    assert "jarvis_response" in data
    assert data["risk_level"] in ["Low", "Moderate", "High", "Critical", "Unknown", "Error"]


def test_ecg_analysis_text():
    """Test ECG analysis with text input."""
    from fastapi.testclient import TestClient
    response = client.post("/api/v1/analyze/ecg",
        data={"text": "Normal sinus rhythm. Heart rate 72 bpm. PR interval normal. QRS normal."})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "findings" in data
    assert "jarvis_response" in data


def test_angioplasty_analysis():
    """Test angioplasty report analysis."""
    report = (
        "Patient underwent successful PCI to the proximal LAD. "
        "One drug-eluting stent (3.0x18mm) was deployed. "
        "TIMI 3 flow achieved. No complications. "
        "Residual stenosis 0%. Previous 90% stenosis."
    )
    response = client.post("/api/v1/analyze/angioplasty",
        data={"report_text": report})
    assert response.status_code == 200
    data = response.json()
    assert "structured_summary" in data
    assert "artery_locations" in data
    assert "LAD" in data["artery_locations"]
    assert "stent_details" in data
    assert "explanation" in data
    assert "jarvis_response" in data


def test_agent_command():
    """Test DeepAgent command endpoint."""
    response = client.post("/api/v1/agent/command", json={
        "message": "Hello JARVIS, how are you?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent_detected" in data
    assert "suggestions" in data


def test_agent_help():
    """Test JARVIS help command."""
    response = client.post("/api/v1/agent/command", json={
        "message": "Help, what can you do?"
    })
    data = response.json()
    assert data["intent_detected"] == "help"
    assert "Heart Attack Risk" in data["response"] or "risk" in data["response"].lower()


def test_data_source_register():
    """Test data source registration."""
    response = client.post("/api/v1/data/source/register", json={
        "source_type": "google_fit",
        "config": {},
        "priority": 3
    })
    assert response.status_code == 200


def test_manual_entry():
    """Test manual vital entry."""
    response = client.post("/api/v1/data/manual", json={
        "heart_rate": 72,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "spo2": 98
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"


def test_generate_demo_data():
    """Test demo data generation."""
    response = client.post("/api/v1/watch/demo/1?days=1")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0


def test_health_summary():
    """Test health summary after demo data."""
    # Generate data first
    client.post("/api/v1/watch/demo/1?days=1")
    response = client.get("/api/v1/monitor/summary/1")
    assert response.status_code == 200
