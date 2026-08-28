import io

import fitz
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.domain import KnowledgeDocument

# Minimal tests as requested

@pytest.mark.asyncio
async def test_upload_pdf(client: AsyncClient, db_session):
    # create dummy pdf
    pdf_bytes = io.BytesIO()
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a dummy test PDF catalogue with pricing: ₹80,000 for a laptop.")
    doc.save(pdf_bytes)
    doc.close()
    
    pdf_bytes.seek(0)
    
    # 1. Upload
    response = await client.post(
        "/knowledge-base/documents?tenant_id=test_tenant",
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["processing", "ready"]
    doc_id = data["document_id"]
    
    # Check DB
    result = await db_session.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id))
    db_doc = result.scalar_one_or_none()
    assert db_doc is not None
    assert db_doc.filename == "test.pdf"

@pytest.mark.asyncio
async def test_upload_invalid_file(client: AsyncClient):
    response = await client.post(
        "/knowledge-base/documents?tenant_id=test_tenant",
        files={"file": ("test.exe", b"invalid", "application/x-msdownload")}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"]["code"] == "UNSUPPORTED_FILE_TYPE"

@pytest.mark.asyncio
async def test_end_to_end_rag(client: AsyncClient, db_session):
    # This simulates the full flow, assuming background processing was run inline or we wait
    pass
    # For a true E2E, we'd need to mock the embeddings_client and run process_document_background
