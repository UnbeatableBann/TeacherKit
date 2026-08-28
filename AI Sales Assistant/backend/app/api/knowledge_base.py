import hashlib

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import KnowledgeDocument
from app.schemas.domain import (
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
    KnowledgeDocumentUploadResponse,
)
from app.services.knowledge_ingestion import process_document_background

router = APIRouter()

SUPPORTED_TYPES = ["application/pdf", "text/csv", "text/plain"]


@router.post("/documents", response_model=KnowledgeDocumentUploadResponse)
async def upload_document(
    tenant_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_FILE", "message": "Filename is required"}},
        )

    content_type = file.content_type
    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "UNSUPPORTED_FILE_TYPE",
                    "message": "This document type is not supported.",
                }
            },
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=400, detail={"error": {"code": "EMPTY_FILE", "message": "File is empty."}}
        )

    # Check for duplicates
    checksum = hashlib.sha256(content).hexdigest()
    existing = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.tenant_id == tenant_id, KnowledgeDocument.checksum == checksum
        )
    )
    existing_doc = existing.scalar_one_or_none()

    if existing_doc:
        # Return existing document per duplication handling policy
        return KnowledgeDocumentUploadResponse(
            document_id=existing_doc.id, status=existing_doc.status
        )

    # Create document record
    doc = KnowledgeDocument(
        tenant_id=tenant_id,
        filename=file.filename,
        content_type=content_type,
        size=len(content),
        status="processing",
        checksum=checksum,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Dispatch background ingestion
    background_tasks.add_task(process_document_background, doc.id, content, content_type, db)

    return KnowledgeDocumentUploadResponse(document_id=doc.id, status=doc.status)


@router.get("/documents", response_model=KnowledgeDocumentListResponse)
async def list_documents(tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.tenant_id == tenant_id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    docs = result.scalars().all()

    return KnowledgeDocumentListResponse(
        documents=[KnowledgeDocumentResponse.model_validate(doc) for doc in docs]
    )


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_document(document_id: str, tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id, KnowledgeDocument.tenant_id == tenant_id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return KnowledgeDocumentResponse.model_validate(doc)


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id, KnowledgeDocument.tenant_id == tenant_id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Mark as deleting
    doc.status = "deleting"
    await db.commit()

    try:
        # DB cascade delete-orphan will handle chunks if we delete the document.
        await db.delete(doc)
        await db.commit()
    except Exception as e:
        await db.rollback()
        # Fallback to failed deletion
        doc.status = "failed"
        doc.metadata_ = {"error": f"Deletion failed: {str(e)}"}
        await db.commit()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "DOCUMENT_DELETION_FAILED",
                    "message": "Failed to delete document completely.",
                }
            },
        )

    return {"status": "success", "message": "Document deleted."}
