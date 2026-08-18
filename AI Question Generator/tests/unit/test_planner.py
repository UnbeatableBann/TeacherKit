import pytest

from app.generation.planner import GenerationPlanner
from app.schemas.domain import GenerateRequest


@pytest.mark.asyncio
async def test_generation_planner_empty_history():
    # Mocking DB session for unit test
    class MockResult:
        def scalars(self):
            class MockScalars:
                def all(self):
                    return []

            return MockScalars()

    class MockDB:
        async def execute(self, stmt):
            return MockResult()

    planner = GenerationPlanner(db=MockDB())

    req = GenerateRequest(subject="Mathematics", class_level="10", total_questions=5)

    plan = await planner.build_plan(req)

    assert plan.total_questions == 5
    assert len(plan.questions) == 5
    # Should fallback to defaults
    assert plan.questions[0].topic == "General"
    assert plan.questions[0].difficulty.value == "Medium"
