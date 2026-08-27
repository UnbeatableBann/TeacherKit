import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.question_analyzer import QuestionAnalyzer
from app.core.database import get_db
from app.extraction.question_extractor import QuestionExtractor
from app.generation.orchestrator import GenerationOrchestrator
from app.ingestion.parser import DocumentParser
from app.llm.gemini import get_embedding
from app.models.domain import Document, Question
from app.schemas.domain import DocumentResponse, GenerateRequest, GenerationResponse

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    subject: Annotated[str, Form(...)],
    class_level: Annotated[str, Form(...)],
    db: DbSession,
):
    try:
        content = await file.read()

        # 1. Create DB Record
        doc = Document(
            id=str(uuid.uuid4()),
            filename=file.filename,
            subject=subject,
            class_level=class_level,
            status="processing",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # 2. Parse PDF
        parser = DocumentParser()
        pages = parser.parse_pdf(content, file.filename)

        # 3. Extract and Analyze Questions
        extractor = QuestionExtractor()
        analyzer = QuestionAnalyzer()

        for page in pages:
            extracted_questions = await extractor.extract_from_text(
                page["text"], page["page_number"]
            )
            for eq in extracted_questions:
                analysis = await analyzer.analyze(eq, subject, class_level)

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

        doc.status = "completed"
        await db.commit()

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generation", response_model=GenerationResponse)
async def generate_questions(
    request: GenerateRequest, db: DbSession
):
    orchestrator = GenerationOrchestrator(db)
    try:
        return await orchestrator.process_generation_request(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
