import enum
import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base


class QuestionCategory(str, enum.Enum):
    OBJECTIVE = "Objective"
    NUMERICAL = "Numerical"
    SUBJECTIVE = "Subjective"


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    MULTIPLE_SELECT = "Multiple Select"
    TRUE_FALSE = "True / False"
    FILL_IN_THE_BLANK = "Fill in the Blank"
    EXACT_ANSWER = "Exact Answer"
    NUMERIC = "Numeric"
    FORMULA = "Formula"
    UNIT_BASED = "Unit-based"
    SHORT_ANSWER = "Short Answer"
    EXPLANATION = "Explanation"
    DESCRIPTIVE = "Descriptive"
    ESSAY = "Essay"
    PROOF = "Proof"
    DERIVATION = "Derivation"


class DifficultyLevel(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str | None] = mapped_column(String)
    class_level: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String, default="pending")
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSONB, default=dict
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    questions: Mapped[list[Question]] = relationship(
        "Question", back_populates="document"
    )


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String, ForeignKey("documents.id"), nullable=False
    )
    source_page: Mapped[int | None] = mapped_column(Integer)
    source_question_number: Mapped[str | None] = mapped_column(String)
    section: Mapped[str | None] = mapped_column(String)

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    marks: Mapped[float | None] = mapped_column(Float)
    options: Mapped[list[Any] | dict[str, Any] | None] = mapped_column(JSONB)
    expected_answer: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    category: Mapped[QuestionCategory | None] = mapped_column(SQLEnum(QuestionCategory))
    question_type: Mapped[QuestionType | None] = mapped_column(SQLEnum(QuestionType))
    topic: Mapped[str | None] = mapped_column(String)
    concepts: Mapped[list[str] | None] = mapped_column(JSONB)
    difficulty: Mapped[DifficultyLevel | None] = mapped_column(SQLEnum(DifficultyLevel))

    provenance: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSIONS)
    )

    document: Mapped[Document] = relationship("Document", back_populates="questions")


class GenerationRequest(Base):
    __tablename__ = "generation_requests"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    subject: Mapped[str] = mapped_column(String, nullable=False)
    class_level: Mapped[str] = mapped_column(String, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_topic: Mapped[str | None] = mapped_column(String)
    requested_difficulty: Mapped[str | None] = mapped_column(String)

    status: Mapped[str | None] = mapped_column(String, default="pending")
    plan_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    generated_questions: Mapped[list[GeneratedQuestion]] = relationship(
        "GeneratedQuestion", back_populates="request"
    )


class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    request_id: Mapped[str] = mapped_column(
        String, ForeignKey("generation_requests.id"), nullable=False
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str | None] = mapped_column(String)
    question_type: Mapped[str | None] = mapped_column(String)
    difficulty: Mapped[str | None] = mapped_column(String)
    marks: Mapped[float | None] = mapped_column(Float)
    answer: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    marking_scheme: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)

    validation_status: Mapped[str | None] = mapped_column(String, default="pending")
    validation_errors: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    similar_to_source_id: Mapped[str | None] = mapped_column(String)

    request: Mapped[GenerationRequest] = relationship(
        "GenerationRequest", back_populates="generated_questions"
    )
