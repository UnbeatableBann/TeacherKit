
from pydantic import BaseModel

from app.llm.gemini import generate_structured
from app.schemas.domain import ExtractedQuestionSchema


class ExtractionResult(BaseModel):
    questions: list[ExtractedQuestionSchema]


class QuestionExtractor:
    async def extract_from_text(
        self, text: str
    ) -> list[ExtractedQuestionSchema]:
        """
        Extracts structured questions from raw document text.
        """
        system_prompt = (
            "You are an expert examination parser. Your task is to extract individual questions "
            "from the provided raw examination text. Preserve the original question text, options (if MCQ), "
            "marks, and question type accurately."
        )

        prompt = f"Extract all questions from the following text:\n\n{text}"

        try:
            result = await generate_structured(
                prompt=prompt,
                response_schema=ExtractionResult,
                system_prompt=system_prompt,
            )
            return result.questions
        except RuntimeError as e:
            # Handle empty or malformed pages gracefully
            print(f"Failed to extract questions: {e}")
            return []
