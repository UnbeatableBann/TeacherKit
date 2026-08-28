import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.generation.orchestrator import GenerationOrchestrator
from app.models.domain import Document
from app.schemas.domain import DocumentResponse, GenerateRequest, GenerationResponse
from app.services.document_processor import process_document_background

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    db: DbSession,
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()

    # Create DB Record
    doc = Document(
        id=str(uuid.uuid4()),
        filename=file.filename,
        status="uploaded",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Trigger background processing
    background_tasks.add_task(
        process_document_background,
        document_id=doc.id,
        content=content,
        filename=file.filename
    )

    return DocumentResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status
    )


@router.get("/documents/{document_id}/status", response_model=DocumentResponse)
async def get_document_status(document_id: str, db: DbSession):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status
    )


@router.post("/generations", response_model=GenerationResponse)
async def generate_questions(
    request: GenerateRequest, db: DbSession
):
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document_id is required.")

    # Validate that all documents exist and are READY
    not_ready = []
    for doc_id in request.document_ids:
        doc = await db.get(Document, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found.")
        if doc.status != "ready":
            not_ready.append({"document_id": doc.id, "status": doc.status})

    if not_ready:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "DOCUMENTS_NOT_READY",
                "message": "One or more documents are still being processed or failed.",
                "documents": not_ready
            }
        )

    # Proceed with generation
    orchestrator = GenerationOrchestrator(db)
    try:
        return await orchestrator.process_generation_request(request)
    except RuntimeError as e:
        # Pass LLM generation errors (like 404 Model Not Found) cleanly to the frontend
        raise HTTPException(status_code=500, detail=str(e))
