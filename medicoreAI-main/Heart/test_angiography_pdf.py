#!/usr/bin/env python3
"""
Test script for Angiography PDF Analysis
Tests the full end-to-end pipeline
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from models.database import SessionLocal
from models.db_models import User
from services.auth_service import hash_password, create_access_token
from io import BytesIO

def create_test_user():
    """Create a test user if it doesn't exist"""
    db = SessionLocal()
    user = db.query(User).filter(User.id == 1).first()
    
    if not user:
        from services.auth_service import hash_password
        user = User(
            id=1,
            username="cardia_test",
            email="test@cardia.health",
            hashed_password=hash_password("test123"),
            full_name="Cardia Test User",
            age=30,
            gender="M",
            role="patient"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Test user created: ID={user.id}")
    else:
        print(f"✅ Test user found: ID={user.id}")
    
    db.close()
    return user

def test_pdf_extraction():
    """Test PDF extraction directly"""
    print("\n📋 Testing PDF Extraction...")
    
    pdf_path = "/Users/sujalnivruttipagere/Desktop/Heart/uploads/ecg_1_1775388325.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        import pypdf
        with open(pdf_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        print(f"✅ PDF extraction successful!")
        print(f"   - Extracted {len(text)} characters")
        print(f"   - Pages: {len(pdf_reader.pages)}")
        print(f"   - Preview: {text[:200]}...")
        return True
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return False

def test_with_curl():
    """Test the API endpoint with curl"""
    print("\n🔗 Testing API Endpoint with curl...")
    
    # Create user first
    user = create_test_user()
    
    # Generate token
    token = create_access_token({"sub": str(user.id), "role": user.role})
    print(f"✅ Generated auth token: {token[:50]}...")
    
    # Test curl request
    import subprocess
    pdf_path = "/Users/sujalnivruttipagere/Desktop/Heart/uploads/ecg_1_1775388325.pdf"
    
    cmd = [
        'curl', '-X', 'POST',
        '-H', f'Authorization: Bearer {token}',
        '-F', f'file=@{pdf_path}',
        'http://localhost:8000/api/v1/analyze/angiography/pdf'
    ]
    
    print(f"Running: {' '.join(cmd[:5])} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ API request successful!")
        print(f"Response: {result.stdout[:300]}...")
        return True
    else:
        print(f"❌ API request failed!")
        print(f"Error: {result.stderr}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Angiography PDF Analysis Test Suite")
    print("=" * 60)
    
    # Test PDF extraction
    pdf_ok = test_pdf_extraction()
    
    # Test API endpoint
    try:
        api_ok = test_with_curl()
    except Exception as e:
        print(f"❌ API test failed with exception: {e}")
        api_ok = False
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ PDF Extraction: {'PASS' if pdf_ok else 'FAIL'}")
    print(f"✅ API Endpoint: {'PASS' if api_ok else 'FAIL'}")
    print("=" * 60)
    
    sys.exit(0 if (pdf_ok and api_ok) else 1)
