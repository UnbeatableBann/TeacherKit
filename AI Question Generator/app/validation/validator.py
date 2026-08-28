from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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

        # Calculate cosine distance and fetch it
        stmt = (
            select(Question.id, Question.embedding.cosine_distance(embedding).label("distance"))
            .order_by("distance")
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.first()

        if row is not None:
            _closest_id, distance = row
            # cosine_distance = 1 - cosine_similarity
            similarity = 1.0 - distance
            if similarity >= settings.SIMILARITY_THRESHOLD:
                return False, f"Question is too similar to historical question (similarity: {similarity:.2f})"

        return True, ""
