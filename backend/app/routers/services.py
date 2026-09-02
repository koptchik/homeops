from fastapi import APIRouter, HTTPException
from backend.app.models import Service, ServiceCreate

router = APIRouter()
services = []
next_id = 1


@router.post("/services")
def create_service(service: ServiceCreate):
    global next_id
    new_service = Service(
        id=next_id,
        name=service.name,
        url=service.url,
        check_interval=service.check_interval
    )
    services.append(new_service)
    next_id += 1
    return new_service

@router.get("/services")
def get_services():
    return services

@router.get("/services/{service_id}")
def get_service(service_id: int):
    for service in services:
        if service_id == service.id:
            return service
    raise HTTPException(
        status_code=404,
        detail="Service not found"
    )

@router.delete("/services/{service_id}")
def delete_service(service_id: int):
    for service in services:
        if service_id == service.id:
            services.remove(service)
            return service
    raise HTTPException(
        status_code=404,
        detail="Service not found"
    )