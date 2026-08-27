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

            # 3. Extract and Analyze Questions
            extractor = QuestionExtractor()
            analyzer = QuestionAnalyzer()

            for page in pages:
                extracted_questions = await extractor.extract_from_text(
                    page["text"], page["page_number"]
                )
                for eq in extracted_questions:
                    # In V2, we might not have subject/class_level yet because they are provided at generation.
                    # We can pass "Unknown" or the document's subject if it was provided, but V2 removes it from upload.
                    analysis = await analyzer.analyze(eq, "Unknown", "Unknown")

                    # Combine extracted & analyzed into DB model
                    db_question = Question(
                        document_id=doc.id,
                        source_page=page["page_number"],
                        question_text=eq.question_text,
                        marks=eq.marks,
                        options=eq.options,
                        category=eq.category,
                        question_type=eq.question_type,
                        topic=analysis.topic if analysis else "General",
                        concepts=analysis.concepts if analysis else [],
                        difficulty=analysis.difficulty if analysis else "Medium",
                        expected_answer=analysis.expected_answer.model_dump()
                        if analysis and analysis.expected_answer
                        else None,
                    )

                    # Compute embedding
                    db_question.embedding = await get_embedding(db_question.question_text)
                    db.add(db_question)

            doc.status = "ready"
            await db.commit()
            logger.info(f"Document {document_id} successfully processed and marked ready.")

        except Exception as e:
            logger.exception(f"Error processing document {document_id}: {e}")
            # Try to mark as failed
            try:
                doc = await db.get(Document, document_id)
                if doc:
                    doc.status = "failed"
                    doc.metadata_ = {"error": str(e)}
                    await db.commit()
            except Exception as inner_e:
                logger.error(f"Failed to update document status to failed: {inner_e}")
