from google import genai
from google.genai import types

from app.config import settings
from app.llm.contract import LLMEvaluator, LLMEvidenceResponse


class GeminiEvaluator(LLMEvaluator):
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def evaluate_answer(self, messages: list[dict[str, str]]) -> LLMEvidenceResponse:
        system_instruction = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_content = next((m["content"] for m in messages if m["role"] == "user"), "")

        response = self.client.models.generate_content(
            model=settings.llm_model,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=user_content)])],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=LLMEvidenceResponse,
                temperature=0.0,
            ),
        )

        parsed = response.parsed
        if not parsed:
            raise ValueError("Failed to parse Gemini structured output")
        if isinstance(parsed, dict):
            return LLMEvidenceResponse(**parsed)
        return parsed  # type: ignore


def get_llm_evaluator() -> LLMEvaluator:
    if settings.llm_provider == "gemini":
        return GeminiEvaluator()
    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}. Only 'gemini' is supported in V1."
    )
