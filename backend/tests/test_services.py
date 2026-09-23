from fastapi.testclient import TestClient
from backend.app.main import app
from pydantic import BaseModel,HttpUrl,ValidationError


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

def test_get_service_999999():
    response = client.get("/services/999999")

    assert response.status_code == 404

def test_delete_service_999999():
    response = client.delete("/services/999999")

    assert response.status_code == 404

def test_service_name_lenht():
    lenghts = [1,2,50,51]
    for lenght in lenghts:
        original_string = "test"
        random_chars = str(abs(hash(original_string))) * 4
        result = random_chars[:lenght]

        response = client.post(
            "/services",
            json={
                "name": result,
                "url": "http://exemple.com:1234",
                "check_interval": 60
            }
        )
        if lenght in range(2,50):
            assert response.status_code == 200
        else:
            assert response.status_code == 422

def test_service_check_interval():
    intervals = [9,10,3600,3601]
    for interval in intervals:
        response = client.post(
            "/services",
            json={
                "name": "test",
                "url": "http://exemple.com:1234",
                "check_interval": interval
            }
        )
        if interval in range(10,3600):
            assert response.status_code == 200
        else:
            assert response.status_code == 422

def test_service_url():
    urls = ["http://exemple.com:1234","exemple com"]
    for url in urls:
        response = client.post(
            "/services",
            json={
                "name": "test",
                "url": url,
                "check_interval": 60
            }
        )
        if url is HttpUrl:
            assert response.status_code == 200
        else:
            assert response.status_code == 422