from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_create_service():
    response = client.post(
        "/services",
        json={
            "name": "test",
            "url": "http://exemple.com:1234",
            "check_interval": 75
        }
    )
    resp = response.json()
    assert response.status_code == 200
    assert resp["name"] == "test"
    assert resp["url"].startswith("http://exemple.com:1234")
    assert resp["check_interval"] == 75
    assert "id" in resp
     