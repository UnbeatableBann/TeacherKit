from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Question


class VectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: list[dict[str, Any]]):
        pass

    @abstractmethod
    async def search(self, query_embedding: list[float], document_ids: list[str], limit: int = 10, threshold: float = 0.7) -> list[dict[str, Any]]:
        pass

class PGVectorStore(VectorStore):
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def add_documents(self, documents: list[dict[str, Any]]):
        pass # Implemented in DocumentProcessor directly for now, or we can move it here.

    async def search(self, query_embedding: list[float], document_ids: list[str], limit: int = 10, threshold: float = 0.7) -> list[dict[str, Any]]:
        # Use cosine distance for semantic similarity mapping
        max_distance = 1.0 - threshold
        
        stmt = (
            select(Question)
            .where(Question.document_id.in_(document_ids))
            .where(Question.embedding.cosine_distance(query_embedding) <= max_distance)
            .order_by(Question.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        questions = result.scalars().all()
        
        # We can rank or additionally filter here if needed, but pgvector handled it
        return [
            {
                "question_text": q.question_text,
                "marks": q.marks,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "question_type": q.question_type.value if q.question_type else None
            }
            for q in questions
        ]
