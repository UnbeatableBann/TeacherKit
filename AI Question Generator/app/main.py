import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.api.endpoints import router as api_router
from app.core.config import settings
from app.core.database import db_manager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up AI Question Generator...")
    db_manager.init_db()
    yield
    # Shutdown actions
    logger.info("Shutting down AI Question Generator...")
    await db_manager.close_db()

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

from fastapi import Request
from fastapi.responses import JSONResponse

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error during {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
