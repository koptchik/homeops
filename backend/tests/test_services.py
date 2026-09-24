from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_create_service():
    jsons=[
        {
            "name": "test",
            "url": "http://exemple.com:1234",
            "check_interval": 75
        },
        {
            "name": "test",
            "url": "http://exemple.com:1234"
        },
        {
            "name": "test"
        },
        {
            "url": "http://exemple.com:1234"
        }
    ]
    for myjson in jsons:
        response = client.post(
            "/services",
            json=myjson,
            )
        data = response.json()
        if "name" in myjson and "url" in myjson:
            assert response.status_code == 200
            assert data["name"] == "test"
            assert data["url"].startswith("http://exemple.com:1234")
            if "check_interval" in myjson:
                assert data["check_interval"] == 75
            else:
                assert data["check_interval"] == 60
            assert "id" in data
        else:
            assert response.status_code == 422
            missing_field =  "name" if "name" not in myjson else "url"
            assert any(error["loc"] == ["body", missing_field] for error in data["detail"])


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
        result = "a" * lenght
        response = client.post(
            "/services",
            json={
                "name": result,
                "url": "http://exemple.com:1234",
                "check_interval": 60
            }
        )
        if 2 <= lenght <= 50:
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
        if 10 <= interval <= 3600:
            assert response.status_code == 200
        else:
            assert response.status_code == 422

def test_service_url():
    case = [("http://exemple.com:1234", 200),("exemple com", 422)]
    for url, expected_status in case:
        response = client.post(
            "/services",
            json={
                "name": "test",
                "url": url,
                "check_interval": 60
            }
        )
        assert response.status_code == expected_status

def test_service_lifecycle():
    created = client.post(
        "/services",
        json={
            "name": "test",
            "url": "http://exemple.com:1234"
        }
    )
    created_id = created.json()["id"]
    assert created.status_code == 200
    assert created.json()["name"] == "test"
    assert created.json()["url"] == "http://exemple.com:1234"
    geted = client.get(f"/services/{created_id}")
    assert geted.status_code == 200
    assert geted.json()["name"] == "test"
    assert geted.json()["url"] == "http://exemple.com:1234"
    deleted = client.delete(f"/services/{created_id}")
    assert deleted.status_code == 200
    assert deleted.json() == created.json()
    not_found = client.get(f"/services/{created_id}")
    assert not_found.status_code == 404
    checked_delete = client.get("/sevices")
    assert created_id not in [item["id"] for item in checked_delete["body"]]

        