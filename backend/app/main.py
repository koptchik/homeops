from fastapi import FastAPI
from backend.app.routers.services import router


app = FastAPI()
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}