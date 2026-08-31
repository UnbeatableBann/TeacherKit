from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums import *

ALLOWED = {
    QuestionCategory.OBJECTIVE: {
        QuestionType.MCQ,
        QuestionType.MULTIPLE_SELECT,
        QuestionType.TRUE_FALSE,
        QuestionType.FILL_IN_THE_BLANK,
        QuestionType.EXACT_ANSWER,
    },
    QuestionCategory.NUMERICAL: {
        QuestionType.NUMERIC,
        QuestionType.FORMULA,
        QuestionType.UNIT_BASED,
    },
    QuestionCategory.SUBJECTIVE: {
        QuestionType.SHORT_ANSWER,
        QuestionType.EXPLANATION,
        QuestionType.DESCRIPTIVE,
        QuestionType.ESSAY,
        QuestionType.PROOF,
        QuestionType.DERIVATION,
    },
}


class QuestionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=50)
    text: str = Field(min_length=1, max_length=2000)


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=10000)
    subject: Subject
    class_level: ClassLevel
    category: QuestionCategory
    type: QuestionType
    options: list[QuestionOption] = Field(default_factory=list)
    marks: float | None = Field(default=None, ge=0)
    expected_unit: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_taxonomy(self) -> Self:
        if self.type not in ALLOWED[self.category]:
            raise ValueError(f"{self.type} does not belong to {self.category}")
        if self.type in {QuestionType.MCQ, QuestionType.MULTIPLE_SELECT} and len(self.options) < 2:
            raise ValueError("MCQ/multiple-select require at least two options")
        if self.type not in {QuestionType.MCQ, QuestionType.MULTIPLE_SELECT} and self.options:
            raise ValueError("Options only allowed for MCQ/multiple-select")
        return self


class ReferenceAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str | None = Field(default=None, max_length=30000)
    accepted_answers: list[str] = Field(default_factory=list)
    correct_option_ids: list[str] = Field(default_factory=list)
    expected_concepts: list[str] = Field(default_factory=list)
    expected_steps: list[str] = Field(default_factory=list)
    rubric: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def nonempty(self) -> Self:
        if not any(
            (
                self.text,
                self.accepted_answers,
                self.correct_option_ids,
                self.expected_concepts,
                self.expected_steps,
                self.rubric,
            )
        ):
            raise ValueError("reference_answer needs at least one evaluation signal")
        return self


class StudentAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(default="", max_length=50000)
    source: AnswerSource = AnswerSource.TEXT
    metadata: dict[str, str | float | int | bool] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def normalize(cls, v: str) -> str:
        return " ".join(v.strip().split())


class EvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: Question
    reference_answer: ReferenceAnswer
    student_answer: StudentAnswer


class Dimension(BaseModel):
    score: float = Field(ge=0, le=100)
    evidence: list[str] = Field(default_factory=list)


class ConceptAnalysis(BaseModel):
    correct: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    incorrect: list[str] = Field(default_factory=list)


class ErrorAnalysis(BaseModel):
    error_type: str | None = None
    severity: str = "none"
    explanation: str | None = None
    distance_from_correct: dict[str, float | str] = Field(default_factory=dict)
    subject_mismatch: bool = False


class Feedback(BaseModel):
    summary: str
    explanation: str
    improvement_hint: str | None = None


class EvaluationResponse(BaseModel):
    status: EvaluationStatus
    score: float | None
    confidence: float
    dimensions: dict[str, Dimension]
    concept_analysis: ConceptAnalysis
    error_analysis: ErrorAnalysis
    feedback: Feedback
    metadata: dict[str, object]
