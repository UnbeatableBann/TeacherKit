import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.generation.generator import QuestionGenerator
from app.generation.planner import GenerationPlanner
from app.schemas.domain import (
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
        plan = await self.planner.build_plan(request)

        generated_questions = []
        for q_plan in plan.questions:
            # Bounded regeneration loop
            for attempt in range(settings.MAX_GENERATION_ATTEMPTS):
                generated = await self.generator.generate_single_question(
                    q_plan, request.subject, request.class_level, request.document_ids
                )

                is_valid, reason = await self.validator.validate(
                    generated, request.subject
                )
                if is_valid:
                    generated.validation_status = "passed"
                    generated_questions.append(generated)
                    break
                elif attempt == settings.MAX_GENERATION_ATTEMPTS - 1:
                    generated.validation_status = f"failed: {reason}"
                    generated_questions.append(generated)

        return GenerationResponse(
            generation_id=str(uuid.uuid4()),
            status="completed",
            subject=request.subject,
            class_level=request.class_level,
            requested_count=request.total_questions,
            generated_count=len(
                [q for q in generated_questions if q.validation_status == "passed"]
            ),
            questions=generated_questions,
        )
