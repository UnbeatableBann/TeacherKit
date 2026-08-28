
from sqlalchemy.ext.asyncio import AsyncSession

from app.generation.generator import QuestionGenerator
from app.generation.planner import GenerationPlanner
from app.models.domain import GeneratedQuestion as DBGeneratedQuestion
from app.models.domain import GenerationRequest as DBGenerationRequest
from app.schemas.domain import (
    GeneratedQuestionResponse,
    GenerateRequest,
    GenerationResponse,
)
from app.validation.validator import QuestionValidator


class GenerationOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.planner = GenerationPlanner(db)
        self.generator = QuestionGenerator(db)
        self.validator = QuestionValidator(db)

    async def process_generation_request(
        self, request: GenerateRequest
    ) -> GenerationResponse:
        db_request = DBGenerationRequest(
            subject=request.subject,
            class_level=request.class_level,
            total_questions=request.total_questions,
            requested_topic=request.requested_topic,
            requested_difficulty=request.requested_difficulty,
            status="processing"
        )
        self.db.add(db_request)
        await self.db.flush()

        plan = await self.planner.build_plan(request)
        db_request.plan_snapshot = plan.model_dump()
        await self.db.flush()

        # Batch generate all questions at once to prevent 429 Too Many Requests
        MAX_ATTEMPTS = 3
        attempts = 0
        
        valid_generated_questions: list[GeneratedQuestionResponse] = []
        all_generated_questions = []
        remaining_plans = plan.questions.copy()
        
        while remaining_plans and attempts < MAX_ATTEMPTS:
            attempts += 1
            try:
                batch_generated = await self.generator.generate_batch_questions(
                    remaining_plans, request.subject, request.class_level, request.document_ids
                )
            except Exception as e:
                db_request.status = "failed"
                await self.db.rollback()
                raise RuntimeError(f"Failed to generate questions: {e}") from e

            new_remaining = []
            for generated, q_plan in zip(batch_generated, remaining_plans):
                # Intra-generation duplication check
                is_intra_dup = any(
                    generated.question_text.strip().lower() == v.question_text.strip().lower() 
                    for v in valid_generated_questions
                )
                
                if is_intra_dup:
                    is_valid = False
                    reason = "Duplicate of another question in this batch"
                else:
                    is_valid, reason = await self.validator.validate(generated, request.subject)

                db_q = DBGeneratedQuestion(
                    request_id=db_request.id,
                    question_text=generated.question_text,
                    topic=generated.topic,
                    question_type=generated.question_type,
                    difficulty=generated.difficulty,
                    marks=generated.marks,
                    answer=generated.answer.model_dump() if generated.answer else None,
                    marking_scheme=[m.model_dump() for m in generated.marking_scheme] if generated.marking_scheme else None
                )

                if is_valid:
                    generated.validation_status = "passed"
                    db_q.validation_status = "passed"
                    valid_generated_questions.append(generated)
                else:
                    generated.validation_status = f"failed: {reason}"
                    db_q.validation_status = "failed"
                    db_q.validation_errors = {"reason": reason}
                    new_remaining.append(q_plan)

                self.db.add(db_q)
                all_generated_questions.append(generated)
                
            remaining_plans = new_remaining

        db_request.status = "completed"
        await self.db.commit()

        return GenerationResponse(
            generation_id=db_request.id,
            status="completed",
            subject=request.subject,
            class_level=request.class_level,
            requested_count=request.total_questions,
            generated_count=len(valid_generated_questions),
            questions=all_generated_questions,
        )
