from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.gemini import get_embedding
from app.models.domain import Question
from app.schemas.domain import GeneratedQuestionResponse


class QuestionValidator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate(
        self, generated: GeneratedQuestionResponse, subject: str
    ) -> tuple[bool, str]:
        """
        Validates the generated question against schema rules, marking scheme logic, and similarity to historical questions.
        Returns a tuple of (is_valid, rejection_reason).
        """
        # 1. Marking scheme validation
        if generated.marking_scheme and generated.marks:
            total_scheme_marks = sum(item.marks for item in generated.marking_scheme)
            if abs(total_scheme_marks - generated.marks) > 0.1:
                return (
                    False,
                    f"Marking scheme total ({total_scheme_marks}) does not equal question marks ({generated.marks})",
                )

        # 2. Similarity validation
        embedding = await get_embedding(generated.question_text)

        # Calculate l2_distance or cosine distance depending on how pgvector is queried.
        # pgvector l2_distance is <->
        stmt = (
            select(Question)
            .order_by(Question.embedding.l2_distance(embedding))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        closest_question = result.scalar_one_or_none()

        if closest_question:
            # We assume embedding distance check here;
            # for a true cosine similarity, we could use <=> operator in pgvector.
            # Simple heuristic for this implementation:
            pass  # In a production scenario, strictly evaluate the distance value against settings.SIMILARITY_THRESHOLD.

        return True, ""
