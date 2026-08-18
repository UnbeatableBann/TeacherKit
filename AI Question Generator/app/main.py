from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Question Generator Platform",
    version="1.0.0",
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok"}
