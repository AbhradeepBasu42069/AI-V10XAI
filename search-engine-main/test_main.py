import pytest
import os
from fastapi.testclient import TestClient
from main import app

# Initialize the test client
client = TestClient(app)

# Use the same key you set in your environment (or auth.py)
VALID_KEY = os.environ.get("MY_API_AUTH_KEY", "fallback_dev_key")

def test_health_check_public():
    """Verify that public routes (if any) are still accessible."""
    response = client.get("/")
    assert response.status_code == 200

def test_parse_resume_no_key():
    """Should return 401 if the X-API-Key header is missing."""
    response = client.post("/resumes/parse", json={"text": "Sample resume"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"

def test_parse_resume_wrong_key():
    """Should return 401 if the X-API-Key is incorrect."""
    headers = {"X-API-Key": "wrong-secret-123"}
    response = client.post("/resumes/parse", json={"text": "Sample resume"}, headers=headers)
    assert response.status_code == 401

def test_parse_resume_success():
    """Should return 200 when the correct key is provided."""
    headers = {"X-API-Key": VALID_KEY}
    # Note: We mock the text because we aren't testing Gemini's capacity here, 
    # just the API's security layer.
    response = client.post("/resumes/parse", json={"text": "John Doe Resume"}, headers=headers)
    assert response.status_code == 200