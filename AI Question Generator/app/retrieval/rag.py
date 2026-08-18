
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.gemini import get_embedding
from app.models.domain import Question


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_historical_context(
        self, topic: str, difficulty: str, limit: int = 3
    ) -> list[Question]:
        """
        Retrieves historical questions for the given topic and difficulty.
        First filters by metadata, then performs a vector search based on the topic semantics
        to find relevant historical examples of how this topic was tested.
        """
        topic_embedding = await get_embedding(
            f"Examination questions about {topic} at {difficulty} difficulty"
        )

        stmt = (
            select(Question)
            .where(Question.topic == topic)
            .where(Question.difficulty == difficulty)
            .order_by(Question.embedding.l2_distance(topic_embedding))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
