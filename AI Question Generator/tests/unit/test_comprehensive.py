import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.generation.planner import GenerationPlanner
from app.schemas.domain import GenerateRequest
from app.analysis.question_analyzer import QuestionAnalyzer
from app.schemas.domain import ExtractedQuestionSchema
from app.validation.validator import QuestionValidator
from app.schemas.domain import GeneratedQuestionResponse
from app.models.domain import DifficultyLevel, QuestionType
from app.core.config import settings

@pytest.mark.asyncio
async def test_planner_distribution():
    # Mocking DB session for unit test
    class MockResult:
        def scalars(self):
            class MockScalars:
                def all(self):
                    # Simulate historical distribution
                    # 6 Medium, 4 Hard -> requested 10 should yield exactly 6 Medium, 4 Hard
                    qs = []
                    class DummyQ:
                        def __init__(self, diff):
                            self.topic = "Algebra"
                            self.difficulty = diff
                            self.question_type = "Short Answer"
                            self.marks = 2.0
                    for _ in range(6): qs.append(DummyQ("Medium"))
                    for _ in range(4): qs.append(DummyQ("Hard"))
                    return qs
            return MockScalars()

    class MockDB:
        async def execute(self, stmt):
            return MockResult()

    planner = GenerationPlanner(db=MockDB())
    req = GenerateRequest(subject="Mathematics", class_level="10", total_questions=10, document_ids=["doc1"])
    plan = await planner.build_plan(req)

    assert plan.total_questions == 10
    mediums = [q for q in plan.questions if q.difficulty.value == "Medium"]
    hards = [q for q in plan.questions if q.difficulty.value == "Hard"]
    assert len(mediums) == 6
    assert len(hards) == 4

@pytest.mark.asyncio
async def test_question_analyzer_returns_data():
    analyzer = QuestionAnalyzer()
    questions = [
        ExtractedQuestionSchema(
            question_text="What is 2+2?",
            options=[],
            marks=1.0,
            question_type=QuestionType.SHORT_ANSWER,
            category="Objective",
            source_page=1
        )
    ]
    
    with patch("app.analysis.question_analyzer.generate_structured") as mock_generate:
        class MockResult:
            results = ["fake_analysis"]
        mock_generate.return_value = MockResult()
        
        results = await analyzer.analyze_batch(questions, "Math", "10")
        assert len(results) == 1
        assert results[0] == "fake_analysis"

@pytest.mark.asyncio
async def test_validator_threshold():
    class MockResult:
        def first(self):
            # Return row with 0.1 cosine distance (0.9 similarity)
            return ("fake_id", 0.1)

    class MockDB:
        async def execute(self, stmt):
            return MockResult()

    validator = QuestionValidator(db=MockDB())
    gen = GeneratedQuestionResponse(
        id="test_123",
        question_text="Duplicate text",
        topic="Math",
        difficulty=DifficultyLevel.EASY,
        marks=1.0,
        question_type=QuestionType.SHORT_ANSWER,
        validation_status="pending"
    )
    
    settings.SIMILARITY_THRESHOLD = 0.85
    with patch("app.validation.validator.get_embedding", return_value=[0.1]*768):
        is_valid, reason = await validator.validate(gen, "Math")
        assert is_valid is False
        assert "similarity: 0.90" in reason
