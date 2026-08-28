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

            # 3 & 4. Chunk pages to prevent LLM JSON truncation (max output tokens)
            extractor = QuestionExtractor()
            analyzer = QuestionAnalyzer()
            extracted_questions = []
            analyses = []
            
            chunk_size = 5
            for i in range(0, len(pages), chunk_size):
                chunk = pages[i : i + chunk_size]
                chunk_text = "\n\n".join([f"--- Page {p['page_number']} ---\n{p['text']}" for p in chunk])
                
                chunk_extracted = await extractor.extract_from_text(chunk_text)
                if chunk_extracted:
                    chunk_analyses = await analyzer.analyze_batch(chunk_extracted, "Unknown", "Unknown")
                    extracted_questions.extend(chunk_extracted)
                    analyses.extend(chunk_analyses)

            # 5. Save to DB
            for eq, analysis in zip(extracted_questions, analyses):
                # We don't have page level granularity for individual questions anymore if they are from full text,
                # but we can just use 1 for now or try to parse section/page if the model returned it.
                # Assuming source_question_number or page is not strictly required.
                
                db_question = Question(
                    document_id=doc.id,
                    source_page=1, # Default to 1 for batched extraction
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
