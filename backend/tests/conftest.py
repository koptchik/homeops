import pytest

from backend.app.routers import services as services_router

@pytest.fixture(autouse=True)
def reset_services():
    services_router.services.clear()
    services_router.next_id = 1

    yield
    
    services_router.services.clear()
    services_router.next_id = 1