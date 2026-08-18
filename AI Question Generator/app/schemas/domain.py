from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.domain import DifficultyLevel, QuestionCategory, QuestionType


class DocumentResponse(BaseModel):
    id: str
    filename: str
    subject: str | None = None
    class_level: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class AnswerSchema(BaseModel):
    correct_option: str | None = None
    explanation: str | None = None
    final_answer: Any | None = None
    unit: str | None = None
    solution_steps: list[str] | None = None
    model_answer: str | None = None
    key_points: list[str] | None = None


class MarkingSchemeItem(BaseModel):
    criteria: str
    marks: float


class ExtractedQuestionSchema(BaseModel):
    question_text: str
    source_question_number: str | None = None
    section: str | None = None
    marks: float | None = None
    options: list[str] | None = None
    category: QuestionCategory
    question_type: QuestionType


class AnalyzedQuestionSchema(BaseModel):
    topic: str
    concepts: list[str]
    difficulty: DifficultyLevel
    expected_answer: AnswerSchema | None = None


class QuestionPlanSchema(BaseModel):
    topic: str
    difficulty: DifficultyLevel
    marks: float
    question_type: QuestionType


class GenerationPlanSchema(BaseModel):
    total_questions: int
    questions: list[QuestionPlanSchema]


class GenerateRequest(BaseModel):
    subject: str
    class_level: str
    total_questions: int
    requested_topic: str | None = None
    requested_difficulty: DifficultyLevel | None = None


class GeneratedQuestionResponse(BaseModel):
    id: str
    question_text: str
    topic: str | None = None
    question_type: str | None = None
    difficulty: str | None = None
    marks: float | None = None
    answer: AnswerSchema | None = None
    marking_scheme: list[MarkingSchemeItem] | None = None
    validation_status: str

    model_config = ConfigDict(from_attributes=True)


class GenerationResponse(BaseModel):
    generation_id: str
    status: str
    subject: str
    class_level: str
    requested_count: int
    generated_count: int
    questions: list[GeneratedQuestionResponse]
