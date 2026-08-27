from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Question
from app.schemas.domain import GenerateRequest, GenerationPlanSchema, QuestionPlanSchema


class GenerationPlanner:
    def __init__(self, db: AsyncSession):
        self.db = db

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

        total_history = len(questions)

        planned_questions: list[QuestionPlanSchema] = []
        for i in range(request.total_questions):
            # Resolve user constraints or fallback to historical majority
            topic = request.requested_topic
            if not topic:
                topic = (
                    max(topic_counts, key=topic_counts.get)
                    if topic_counts
                    else "General"
                )

            difficulty = request.requested_difficulty
            if not difficulty:
                difficulty = (
                    max(difficulty_counts, key=difficulty_counts.get)
                    if difficulty_counts
                    else "Medium"
                )

            q_type = (
                max(type_counts, key=type_counts.get) if type_counts else "Short Answer"
            )
            marks = max(marks_counts, key=marks_counts.get) if marks_counts else 2.0

            planned_questions.append(
                QuestionPlanSchema(
                    topic=topic,
                    difficulty=difficulty,
                    marks=marks,
                    question_type=q_type,
                )
            )

        return GenerationPlanSchema(
            total_questions=request.total_questions, questions=planned_questions
        )
