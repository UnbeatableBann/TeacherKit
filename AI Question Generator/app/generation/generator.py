from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.gemini import generate_structured
from app.retrieval.rag import RAGService
from app.schemas.domain import GeneratedQuestionResponse, QuestionPlanSchema


class QuestionGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = RAGService(db)

    async def generate_single_question(
        self, plan: QuestionPlanSchema, subject: str, class_level: str, document_ids: list[str]
    ) -> GeneratedQuestionResponse:
        """
        Generates a single question based on the plan and retrieved historical context.
        """
        historical_context = await self.rag.retrieve_historical_context(
            plan.topic, plan.difficulty.value, document_ids
        )
        context_str = "\n".join(
            [f"- {q.question_text} (Marks: {q.marks})" for q in historical_context]
        )

        system_prompt = (
            f"You are an expert {subject} educator for class level {class_level}. "
            "Generate a BRAND NEW, original question that strictly follows the requested topic, difficulty, and marks. "
            "Use the provided historical questions ONLY as style/pattern references. DO NOT copy them."
        )

        prompt = (
            f"Topic: {plan.topic}\n"
            f"Difficulty: {plan.difficulty.value}\n"
            f"Marks: {plan.marks}\n"
            f"Question Type: {plan.question_type.value}\n\n"
            f"Historical Reference Questions:\n{context_str}\n\n"
            "Generate a new question, its answer, and a marking scheme."
        )

        return await generate_structured(
            prompt=prompt,
            response_schema=GeneratedQuestionResponse,
            system_prompt=system_prompt,
        )
