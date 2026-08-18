import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
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
from sqlalchemy.orm import relationship

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
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    subject = Column(String)
    class_level = Column(String)
    status = Column(String, default="pending")
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="document")


class Question(Base):
    __tablename__ = "questions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    source_page = Column(Integer)
    source_question_number = Column(String)
    section = Column(String)

    question_text = Column(Text, nullable=False)
    marks = Column(Float)
    options = Column(JSONB)
    expected_answer = Column(JSONB)

    category = Column(SQLEnum(QuestionCategory))
    question_type = Column(SQLEnum(QuestionType))
    topic = Column(String)
    concepts = Column(JSONB)
    difficulty = Column(SQLEnum(DifficultyLevel))

    provenance = Column(JSONB)
    embedding = Column(Vector(768))  # Gemini uses 768 dimensions

    document = relationship("Document", back_populates="questions")


class GenerationRequest(Base):
    __tablename__ = "generation_requests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String, nullable=False)
    class_level = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    requested_topic = Column(String)
    requested_difficulty = Column(String)

    status = Column(String, default="pending")
    plan_snapshot = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    generated_questions = relationship("GeneratedQuestion", back_populates="request")


class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("generation_requests.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    topic = Column(String)
    question_type = Column(String)
    difficulty = Column(String)
    marks = Column(Float)
    answer = Column(JSONB)
    marking_scheme = Column(JSONB)

    validation_status = Column(String, default="pending")
    validation_errors = Column(JSONB)
    similar_to_source_id = Column(String)

    request = relationship("GenerationRequest", back_populates="generated_questions")
