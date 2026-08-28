import logging
from typing import Any, Dict, List

import fitz  # PyMuPDF
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings_client import get_embeddings
from app.models.domain import KnowledgeChunk, KnowledgeDocument

logger = logging.getLogger(__name__)

class ChunkData(BaseModel):
    chunk_index: int
    content: str
    page_number: int | None = None
    section: str | None = None
    metadata_: Dict[str, Any] = {}

def extract_text_from_pdf(content_bytes: bytes) -> List[ChunkData]:
    """Parse PDF and extract text with page provenance."""
    doc = fitz.open(stream=content_bytes, filetype="pdf")
    chunks = []
    chunk_idx = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if not text:
            continue
            
        # Basic chunking: split by paragraphs or max length if too long. 
        # For simplicity, we chunk per page, but if a page is > 1000 chars, we split it.
        #TODO: A more sophisticated chunker would be semantic, but this satisfies the provenance requirement.
        max_length = 2000
        
        # Split by double newline to approximate paragraphs
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if len(current_chunk) + len(para) > max_length:
                if current_chunk:
                    chunks.append(ChunkData(
                        chunk_index=chunk_idx,
                        content=current_chunk.strip(),
                        page_number=page_num + 1
                    ))
                    chunk_idx += 1
                    current_chunk = ""
            
            current_chunk += para + "\n\n"
            
        if current_chunk.strip():
            chunks.append(ChunkData(
                chunk_index=chunk_idx,
                content=current_chunk.strip(),
                page_number=page_num + 1
            ))
            chunk_idx += 1

    return chunks

async def process_document_background(
    document_id: str,
    content_bytes: bytes,
    content_type: str,
    db: AsyncSession
):
    """
    Background worker function for document ingestion.
    Parses, chunks, embeds, and persists document chunks in transaction.
    """
    try:
        # 1. Parse and chunk
        if content_type == "application/pdf":
            chunks_data = extract_text_from_pdf(content_bytes)
        elif content_type in ["text/plain", "text/csv"]:
            text = content_bytes.decode("utf-8", errors="replace")
            # Simple chunking for text
            chunks_data = [ChunkData(chunk_index=0, content=text[:5000])] # simplified for text
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

        if not chunks_data:
            raise ValueError("No extractable text found in document.")

        # 2. Batch generate embeddings
        texts_to_embed = [c.content for c in chunks_data]
        
        # Batch requests to avoid hitting API limits or large payloads
        batch_size = 50
        all_embeddings = []
        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i + batch_size]
            embeddings = await get_embeddings(batch_texts)
            all_embeddings.extend(embeddings)

        if len(all_embeddings) != len(chunks_data):
            raise RuntimeError("Embedding count mismatch.")

        # 3. Persist transactionally
        # We need to fetch the document to update status and add chunks
        result = await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == document_id))
        doc = result.scalar_one_or_none()
        
        if not doc:
            logger.error(f"Document {document_id} not found during processing.")
            return

        for chunk_data, emb in zip(chunks_data, all_embeddings):
            chunk = KnowledgeChunk(
                document_id=doc.id,
                chunk_index=chunk_data.chunk_index,
                content=chunk_data.content,
                page_number=chunk_data.page_number,
                section=chunk_data.section,
                metadata_=chunk_data.metadata_,
                embedding=emb
            )
            db.add(chunk)
            
        doc.status = "ready"
        await db.commit()
        logger.info(f"Successfully processed document {document_id} with {len(chunks_data)} chunks.")

    except Exception as e:
        logger.exception(f"Failed to process document {document_id}")
        await db.rollback()
        
        # Mark as failed
        result = await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == document_id))
        doc = result.scalar_one_or_none()
        if doc:
            doc.status = "failed"
            # save error in metadata
            doc.metadata_ = {"error": str(e)}
            await db.commit()
