from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import catalogue, conversations, escalations, leads

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up AI Sales Assistant Backend")
    yield
    log.info("Shutting down AI Sales Assistant Backend")


app = FastAPI(title="AI Sales Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(leads.router, prefix="/leads", tags=["leads"])
app.include_router(catalogue.router, prefix="/catalogue", tags=["catalogue"])
app.include_router(escalations.router, prefix="/escalations", tags=["escalations"])



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception(
        "unhandled_server_error", method=request.method, path=request.url.path, exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
