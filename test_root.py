#!/usr/bin/env python3
"""Test module for the root route functionality."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_html_response():
    """Test that root endpoint returns HTML when requested."""
    response = client.get("/", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"Secure Agent Scheduler" in response.content
    assert b"Audit Log" in response.content

def test_health_endpoint_still_works():
    """Test that existing health endpoint remains functional."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "secure-agent-scheduler"

def test_docs_endpoint_still_works():
    """Test that API documentation endpoint remains functional."""
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

if __name__ == "__main__":
    # Run basic tests
    print("Running tests for root route...")
    
    test_root_html_response()  
    print("✅ HTML response test passed")
    
    test_health_endpoint_still_works()
    print("✅ Health endpoint test passed")
    
    test_docs_endpoint_still_works()
    print("✅ Docs endpoint test passed")
    
    print("\n🎉 All tests passed!")
