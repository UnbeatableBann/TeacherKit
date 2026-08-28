from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import DifficultyLevel, Question, QuestionType
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

        planned_questions: list[QuestionPlanSchema] = []
        for i in range(request.total_questions):
            # Resolve user constraints or fallback to historical majority
            topic = request.requested_topic
            if not topic:
                topic = (
                    max(topic_counts, key=lambda k: topic_counts[k])
                    if topic_counts
                    else "General"
                )

            difficulty = request.requested_difficulty
            if not difficulty:
                diff_str = (
                    max(difficulty_counts, key=lambda k: difficulty_counts[k])
                    if difficulty_counts
                    else "Medium"
                )
                # Cast the string to DifficultyLevel if it matches, otherwise use Medium
                try:
                    difficulty = DifficultyLevel(diff_str)
                except ValueError:
                    difficulty = DifficultyLevel.MEDIUM

            q_type_str = (
                max(type_counts, key=lambda k: type_counts[k]) if type_counts else "Short Answer"
            )
            try:
                q_type = QuestionType(q_type_str)
            except ValueError:
                q_type = QuestionType.SHORT_ANSWER

            marks = max(marks_counts, key=lambda k: marks_counts[k]) if marks_counts else 2.0

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
