import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.api.endpoints import router as api_router
from app.core.config import settings
from app.core.database import engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up AI Question Generator...")
    yield
    # Shutdown actions
    logger.info("Shutting down AI Question Generator...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Question Generator Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # We will use Scalar instead of standard Swagger UI
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
