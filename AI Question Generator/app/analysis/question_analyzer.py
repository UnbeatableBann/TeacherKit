
from app.llm.gemini import generate_structured
from app.schemas.domain import AnalyzedQuestionSchema, ExtractedQuestionSchema


class QuestionAnalyzer:
    async def analyze(
        self, question: ExtractedQuestionSchema, subject: str, class_level: str
    ) -> AnalyzedQuestionSchema | None:
        """
        Analyzes an extracted question to determine topic, concepts, difficulty, and expected answer.
        """
        system_prompt = (
            f"You are an expert {subject} educator for class level {class_level}. "
            "Analyze the provided question and return structured metadata including the exact topic, "
            "key concepts tested, difficulty level, and expected answer structure. "
            "Base difficulty on required reasoning depth, number of steps, and conceptual complexity."
        )

        prompt = (
            f"Question: {question.question_text}\n"
            f"Type: {question.question_type.value}\n"
            f"Marks: {question.marks}\n"
            f"Options: {question.options}\n"
        )

        try:
            return await generate_structured(
                prompt=prompt,
                response_schema=AnalyzedQuestionSchema,
                system_prompt=system_prompt,
            )
        except Exception as e:
            print(f"Failed to analyze question: {e}")
            return None
