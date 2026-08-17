from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class LLMEvidenceResponse(BaseModel):
    score: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="The score awarded (0-100) based on correctness and completeness.",
    )
    recognized_concepts: list[str] = Field(
        default_factory=list, description="Concepts successfully demonstrated in the answer."
    )
    missing_concepts: list[str] = Field(
        default_factory=list, description="Expected concepts that are missing from the answer."
    )
    detected_misconceptions: list[str] = Field(
        default_factory=list,
        description="Any fundamental misunderstandings or incorrect statements.",
    )
    explanation: str = Field(description="Detailed explanation of the grading.")
    error_type: str | None = Field(
        default=None,
        description="The primary error type (e.g., missing_concept, incorrect_concept, incomplete_reasoning, invalid_reasoning, factual_error, grammar_issue, irrelevant_response, prompt_injection, incomplete_response)",
    )
    improvement_guidance: str | None = Field(
        default=None, description="Hints or feedback for the student on how to improve."
    )


class LLMEvaluator(ABC):
    @abstractmethod
    def evaluate_answer(self, messages: list[dict[str, str]]) -> LLMEvidenceResponse:
        pass
