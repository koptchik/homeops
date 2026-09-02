from pydantic import BaseModel, Field, HttpUrl

class ServiceCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )
    url: HttpUrl
    check_interval: int = Field(
        60,
        ge=10,
        le=3600
    )

class Service(BaseModel):
    id: int
    name: str
    url: HttpUrl
    check_interval: int