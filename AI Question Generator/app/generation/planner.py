from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import DifficultyLevel, Question, QuestionType
from app.schemas.domain import GenerateRequest, GenerationPlanSchema, QuestionPlanSchema


class GenerationPlanner:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _allocate(self, counts: dict, total: int, default: Any) -> list:
        if not counts:
            return [default] * total
            
        total_historical = sum(counts.values())
        allocation = {}
        remainders = {}
        
        for k, v in counts.items():
            exact = (v / total_historical) * total
            allocation[k] = int(exact)
            remainders[k] = exact - int(exact)
            
        allocated_total = sum(allocation.values())
        
        # distribute remainder
        sorted_remainders = sorted(remainders.keys(), key=lambda k: remainders[k], reverse=True)
        for i in range(total - allocated_total):
            allocation[sorted_remainders[i % len(sorted_remainders)]] += 1
            
        result = []
        for k, count in allocation.items():
            result.extend([k] * count)
        return result

    async def build_plan(self, request: GenerateRequest) -> GenerationPlanSchema:
        """
        Builds a generation plan based on historical patterns or explicit user constraints.
        """
        # Fetch historical questions for the selected documents
        stmt = select(Question).where(
            Question.document_id.in_(request.document_ids)
        )
        result = await self.db.execute(stmt)
        questions = result.scalars().all()

        # Calculate historical distributions
        topic_counts: dict[str, int] = defaultdict(int)
        difficulty_counts: dict[str, int] = defaultdict(int)
        type_counts: dict[str, int] = defaultdict(int)
        marks_counts: dict[float, int] = defaultdict(int)

        for q in questions:
            if q.topic:
                topic_counts[q.topic] += 1
            if q.difficulty:
                difficulty_counts[q.difficulty] += 1
            if q.question_type:
                type_counts[q.question_type] += 1
            if q.marks:
                marks_counts[q.marks] += 1

        total = request.total_questions
        
        if request.requested_topic:
            allocated_topics = [request.requested_topic] * total
        else:
            allocated_topics = self._allocate(topic_counts, total, "General")
            
        if request.requested_difficulty:
            try:
                diff_val = DifficultyLevel(request.requested_difficulty)
            except ValueError:
                diff_val = DifficultyLevel.MEDIUM
            allocated_diffs = [diff_val] * total
        else:
            diff_strs = self._allocate(difficulty_counts, total, "Medium")
            allocated_diffs = []
            for d in diff_strs:
                try:
                    allocated_diffs.append(DifficultyLevel(d))
                except ValueError:
                    allocated_diffs.append(DifficultyLevel.MEDIUM)

        type_strs = self._allocate(type_counts, total, "Short Answer")
        allocated_types = []
        for t in type_strs:
            try:
                allocated_types.append(QuestionType(t))
            except ValueError:
                allocated_types.append(QuestionType.SHORT_ANSWER)

        allocated_marks = self._allocate(marks_counts, total, 2.0)

        planned_questions: list[QuestionPlanSchema] = []
        for i in range(total):
            planned_questions.append(
                QuestionPlanSchema(
                    topic=allocated_topics[i],
                    difficulty=allocated_diffs[i],
                    marks=allocated_marks[i],
                    question_type=allocated_types[i],
                )
            )

        return GenerationPlanSchema(
            total_questions=total, questions=planned_questions
        )
