from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.gemini import generate_structured
from app.retrieval.rag import RAGService
from app.schemas.domain import GeneratedQuestionResponse, QuestionPlanSchema


from typing import List
from pydantic import BaseModel

class BatchGenerationResponse(BaseModel):
    questions: list[GeneratedQuestionResponse]

class QuestionGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = RAGService(db)

    async def generate_batch_questions(
        self, plans: list[QuestionPlanSchema], subject: str, class_level: str, document_ids: list[str]
    ) -> list[GeneratedQuestionResponse]:
        """
        Generates a batch of questions based on the plans to save LLM calls.
        """
        if not plans:
            return []
            
        # For simplicity, assuming the plans are homogeneous (which they currently are in planner)
        # We just grab the context for the first plan.
        historical_context = await self.rag.retrieve_historical_context(
            plans[0].topic, plans[0].difficulty.value, document_ids
        )
        context_str = "\n".join(
            [f"- {q.question_text} (Marks: {q.marks})" for q in historical_context]
        )

        system_prompt = (
            f"You are an expert {subject} educator for class level {class_level}. "
            f"Generate {len(plans)} BRAND NEW, original questions that strictly follow the requested parameters. "
            "Use the provided historical questions ONLY as style/pattern references. DO NOT copy them."
        )

        prompt_lines = []
        for i, plan in enumerate(plans):
            prompt_lines.append(f"--- Question {i+1} Specs ---")
            prompt_lines.append(f"Topic: {plan.topic}")
            prompt_lines.append(f"Difficulty: {plan.difficulty.value}")
            prompt_lines.append(f"Marks: {plan.marks}")
            prompt_lines.append(f"Question Type: {plan.question_type.value}\n")
            
        prompt = (
            "\n".join(prompt_lines) +
            f"\nHistorical Reference Questions:\n{context_str}\n\n"
            f"Generate exactly {len(plans)} new questions, along with their answers and marking schemes."
        )

        result = await generate_structured(
            prompt=prompt,
            response_schema=BatchGenerationResponse,
            system_prompt=system_prompt,
        )
        return result.questions


