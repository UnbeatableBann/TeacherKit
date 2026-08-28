from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import Question
from sqlalchemy import select

class VectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Dict[str, Any]]):
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], document_ids: List[str], topic: str, difficulty: str, limit: int = 3) -> List[Dict[str, Any]]:
        pass

class PGVectorStore(VectorStore):
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def add_documents(self, documents: List[Dict[str, Any]]):
        pass # Implemented in DocumentProcessor directly for now, or we can move it here.

    async def search(self, query_embedding: List[float], document_ids: List[str], topic: str, difficulty: str, limit: int = 3) -> List[Dict[str, Any]]:
        stmt = (
            select(Question)
            .where(Question.document_id.in_(document_ids))
            .where(Question.topic == topic)
            .where(Question.difficulty == difficulty)
            .order_by(Question.embedding.l2_distance(query_embedding))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        questions = result.scalars().all()
        return [
            {
                "question_text": q.question_text,
                "marks": q.marks,
                "topic": q.topic,
                "difficulty": q.difficulty
            }
            for q in questions
        ]
