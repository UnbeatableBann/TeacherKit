
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.llm.gemini import get_embedding
from app.retrieval.vector_store import PGVectorStore


class RAGService:
    def __init__(self, db: AsyncSession):
        # In the future, this can be instantiated based on VECTOR_DATABASE_URL
        self.vector_store = PGVectorStore(db)

    async def retrieve_historical_context(
        self, topic: str, difficulty: str, document_ids: list[str], limit: int = 5
    ) -> list[dict]:
        """
        Retrieves historical questions for the given topic and difficulty using semantic similarity.
        """
        topic_embedding = await get_embedding(
            f"Examination questions about {topic} at {difficulty} difficulty"
        )

        return await self.vector_store.search(
            query_embedding=topic_embedding,
            document_ids=document_ids,
            limit=limit,
            threshold=settings.SIMILARITY_THRESHOLD
        )
