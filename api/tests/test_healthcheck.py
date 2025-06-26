from fastapi.testclient import TestClient
from api import app

def test_healthcheck():
    client = TestClient(app)
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "uptime" in data
    assert isinstance(data["uptime"], dict) 