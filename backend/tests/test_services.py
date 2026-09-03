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
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "test"
    assert data["url"].startswith("http://exemple.com:1234")
    assert data["check_interval"] == 75
    assert "id" in data

def test_get_services():
    response = client.post(
        "/services",
        json={
            "name": "service-one",
            "url": "https://example.com",
            "check_interval": 60,
        },
    )

    created = response.json()

    response = client.get("/services")
    data = response.json()

    assert response.status_code == 200
    assert created in data

def test_get_service():
    create_response = client.post(
        "/services",
        json={
            "name": "test-service",
            "url": "https://example.com",
            "check_interval": 60,
        },
    )

    created = create_response.json()
    service_id = created["id"]

    response = client.get(f"/services/{service_id}")

    assert response.status_code == 200
    assert response.json() == created

def test_delete_service():
    create_response = client.post(
        "/services",
        json={
            "name": "delete-me",
            "url": "https://example.com",
            "check_interval": 60,
        },
    )

    created = create_response.json()

    response = client.delete(f"/services/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created