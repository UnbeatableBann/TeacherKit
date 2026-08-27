import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.llm.contract import LLMEvidenceResponse
from app.main import app

client = TestClient(app)


def test_subjective_llm_evaluation():
    payload = {
        "question": {
            "id": "q1",
            "text": "Explain why ice floats on water.",
            "subject": "science",
            "class_level": "std_8",
            "category": "subjective",
            "type": "explanation",
        },
        "reference_answer": {
            "text": "Ice floats because it is less dense than liquid water due to its molecular structure.",
            "expected_concepts": ["density", "hydrogen bonds", "less dense"],
        },
        "student_answer": {"content": "Ice is lighter than water so it floats.", "source": "text"},
    }

    mock_response = LLMEvidenceResponse(
        score=50.0,
        recognized_concepts=["mock_concept"],
        missing_concepts=[],
        detected_misconceptions=[],
        explanation="Mock explanation",
        improvement_guidance="Mock guidance",
    )

    with patch("app.strategies.llm.get_llm_evaluator") as mock_get_evaluator:
        mock_evaluator_instance = mock_get_evaluator.return_value
        mock_evaluator_instance.evaluate_answer.return_value = mock_response

        response = client.post("/api/v1/evaluations", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "llm_evaluation" in data["metadata"]["strategies"]

        assert data["concept_analysis"]["correct"] != []
        assert "mock_concept" in data["concept_analysis"]["correct"]


def test_objective_llm_not_interfering_exact_match():
    payload = {
        "question": {
            "id": "q2",
            "text": "Which planet is known as the Red Planet?",
            "subject": "science",
            "class_level": "std_5",
            "category": "objective",
            "type": "mcq",
            "options": [{"id": "A", "text": "Earth"}, {"id": "B", "text": "Mars"}],
        },
        "reference_answer": {"text": "Mars", "correct_option_ids": ["B"]},
        "student_answer": {"content": "B", "source": "text"},
    }

    # We shouldn't even call the LLM because it's objective, but we can mock it just in case
    with patch("app.strategies.llm.get_llm_evaluator"):
        response = client.post("/api/v1/evaluations", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "correct"
        assert data["score"] == 100.0


@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="Requires GEMINI_API_KEY")
def test_gemini_integration():
    os.environ["LLM_PROVIDER"] = "gemini"

    payload = {
        "question": {
            "id": "q3",
            "text": "Explain why ice floats on water.",
            "subject": "science",
            "class_level": "std_8",
            "category": "subjective",
            "type": "explanation",
        },
        "reference_answer": {
            "text": "Ice floats because it is less dense than liquid water due to its molecular structure (hydrogen bonds).",
            "expected_concepts": ["density", "hydrogen bonds"],
        },
        "student_answer": {
            "content": "Ice floats because it forms a lattice that takes up more space, making it less dense.",
            "source": "text",
        },
    }

    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "mock_concept" not in data["concept_analysis"]["correct"]
    assert "density" in " ".join(data["concept_analysis"]["correct"]).lower()
