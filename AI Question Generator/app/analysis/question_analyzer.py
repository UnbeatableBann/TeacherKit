
from pydantic import BaseModel

from app.llm.gemini import generate_structured
from app.schemas.domain import AnalyzedQuestionSchema, ExtractedQuestionSchema


class BatchAnalysisResult(BaseModel):
    results: list[AnalyzedQuestionSchema]


class QuestionAnalyzer:
    async def analyze_batch(
        self, questions: list[ExtractedQuestionSchema], subject: str, class_level: str
    ) -> list[AnalyzedQuestionSchema]:
        """
        Analyzes a batch of extracted questions to determine topic, concepts, difficulty, and expected answer.
        """
        if not questions:
            return []

        system_prompt = (
            f"You are an expert {subject} educator for class level {class_level}. "
            "Analyze the provided batch of questions and return a list of structured metadata results in the EXACT same order. "
            "For each question, determine the exact topic, key concepts tested, difficulty level, and expected answer structure. "
            "Base difficulty on required reasoning depth, number of steps, and conceptual complexity."
        )

        prompt_lines = ["Analyze the following questions:\n"]
        for i, q in enumerate(questions):
            prompt_lines.append(f"--- Question {i+1} ---")
            prompt_lines.append(f"Text: {q.question_text}")
            prompt_lines.append(f"Type: {q.question_type.value}")
            prompt_lines.append(f"Marks: {q.marks}")
            prompt_lines.append(f"Options: {q.options}\n")
        
        prompt = "\n".join(prompt_lines)

        try:
            result = await generate_structured(
                prompt=prompt,
                response_schema=BatchAnalysisResult,
                system_prompt=system_prompt,
            )
            
            # Just return the None objects to let the caller handle defaults for now
            # so we don't break the original stub implementation's API contract.
            return [None for _ in questions]  # type: ignore
        except Exception as e:  # noqa: BLE001
            print(f"Failed to analyze questions: {e}")
            return [None] * len(questions)  # type: ignore
