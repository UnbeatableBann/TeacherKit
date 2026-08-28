from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import conversations, escalations, knowledge_base, leads

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up AI Sales Assistant Backend")
    yield
    log.info("Shutting down AI Sales Assistant Backend")


app = FastAPI(title="AI Sales Assistant API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(escalations.router, prefix="/escalations", tags=["Escalations"])
app.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["Knowledge Base"])



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
