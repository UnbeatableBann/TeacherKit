
from pydantic import BaseModel

from app.llm.gemini import generate_structured
from app.schemas.domain import ExtractedQuestionSchema


class ExtractionResult(BaseModel):
    questions: list[ExtractedQuestionSchema]


class QuestionExtractor:
    async def extract_from_text(
        self, text: str, page_number: int
    ) -> list[ExtractedQuestionSchema]:
        """
        Extracts structured questions from raw page text.
        """
        system_prompt = (
            "You are an expert examination parser. Your task is to extract individual questions "
            "from the provided raw examination text. Preserve the original question text, options (if MCQ), "
            "marks, and question type accurately."
        )

        prompt = f"Extract all questions from the following text (Page {page_number}):\n\n{text}"

        try:
            result = await generate_structured(
                prompt=prompt,
                response_schema=ExtractionResult,
                system_prompt=system_prompt,
            )
            return result.questions
        except Exception as e:  # noqa: BLE001
            # Handle empty or malformed pages gracefully
            print(f"Failed to extract questions: {e}")
            return []
