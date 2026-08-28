import logging

from app.analysis.question_analyzer import QuestionAnalyzer
from app.core.database import db_manager
from app.extraction.question_extractor import QuestionExtractor
from app.ingestion.parser import DocumentParser
from app.llm.gemini import get_embedding
from app.models.domain import Document, Question

logger = logging.getLogger(__name__)

async def process_document_background(document_id: str, content: bytes, filename: str):
    """
    Background task to process a document:
    Extract text -> Extract questions -> Analyze -> Compute Embeddings -> Save to DB.
    """
    if db_manager.session_maker is None:
        logger.error("Database not initialized for background task.")
        return

    async with db_manager.session_maker() as db:
        try:
            # 1. Fetch document to ensure it exists and update status
            doc = await db.get(Document, document_id)
            if not doc:
                logger.error(f"Document {document_id} not found in DB.")
                return

            doc.status = "processing"
            await db.commit()

            # 2. Parse PDF
            parser = DocumentParser()
            pages = parser.parse_pdf(content, filename)

            # 3. Just mark the document as ready. The user requested to skip LLM extraction during upload.
            # In the future, we will extract or process the document during generation or store raw chunks.
            doc.status = "ready"
            await db.commit()
            logger.info(f"Document {document_id} successfully uploaded and marked ready (Skipped LLM extraction).")

        except Exception as e:
            logger.exception(f"Error processing document {document_id}")
            # Try to mark as failed
            try:
                doc = await db.get(Document, document_id)
                if doc:
                    doc.status = "failed"
                    doc.metadata_ = {"error": str(e)}
                    await db.commit()
            except Exception as inner_e:  # noqa: BLE001
                logger.error(f"Failed to update document status to failed: {inner_e}")
