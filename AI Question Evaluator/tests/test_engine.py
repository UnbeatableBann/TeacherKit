from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_mcq_correct():
    p = {
        "question": {
            "id": "q1",
            "text": "Red Planet?",
            "subject": "science",
            "class_level": "std_5",
            "category": "objective",
            "type": "mcq",
            "options": [{"id": "A", "text": "Earth"}, {"id": "B", "text": "Mars"}],
        },
        "reference_answer": {"text": "Mars", "correct_option_ids": ["B"]},
        "student_answer": {"content": "B", "source": "text"},
    }
    r = client.post("/api/v1/evaluations", json=p)
    assert r.status_code == 200
    assert r.json()["status"] == "correct"
    assert r.json()["score"] == 100


def test_mcq_wrong_explains():
    p = {
        "question": {
            "id": "q1",
            "text": "Red Planet?",
            "subject": "science",
            "class_level": "std_5",
            "category": "objective",
            "type": "mcq",
            "options": [{"id": "A", "text": "Earth"}, {"id": "B", "text": "Mars"}],
        },
        "reference_answer": {"text": "Mars", "correct_option_ids": ["B"]},
        "student_answer": {"content": "A", "source": "text"},
    }
    d = client.post("/api/v1/evaluations", json=p).json()
    assert d["status"] == "incorrect"
    assert d["error_analysis"]["error_type"] == "incorrect_selection_or_answer"
    assert "Expected" in d["feedback"]["explanation"]


def test_multiple_select_partial():
    p = {
        "question": {
            "id": "q2",
            "text": "Mammals?",
            "subject": "science",
            "class_level": "std_5",
            "category": "objective",
            "type": "multiple_select",
            "options": [
                {"id": "A", "text": "Dog"},
                {"id": "B", "text": "Whale"},
                {"id": "C", "text": "Shark"},
                {"id": "D", "text": "Cat"},
            ],
        },
        "reference_answer": {"correct_option_ids": ["A", "B", "D"]},
        "student_answer": {"content": "A,B", "source": "text"},
    }
    d = client.post("/api/v1/evaluations", json=p).json()
    assert d["status"] == "partially_correct"


def test_numeric_distance():
    p = {
        "question": {
            "id": "m1",
            "text": "12x5",
            "subject": "mathematics",
            "class_level": "std_5",
            "category": "numerical",
            "type": "numeric",
        },
        "reference_answer": {"text": "60"},
        "student_answer": {"content": "50", "source": "text"},
    }
    d = client.post("/api/v1/evaluations", json=p).json()
    assert d["error_analysis"]["distance_from_correct"]["absolute_error"] == 10

def test_subjective_uses_multiple_strategies():
    p = {
        "question": {
            "id": "s1",
            "text": "Why does ice float?",
            "subject": "science",
            "class_level": "std_8",
            "category": "subjective",
            "type": "explanation",
        },
        "reference_answer": {
            "text": "Ice is less dense than liquid water.",
            "expected_concepts": ["less dense", "liquid water"],
        },
        "student_answer": {
            "content": "Ice floats because it is less dense than liquid water.",
            "source": "text",
        },
    }
    d = client.post("/api/v1/evaluations", json=p).json()
    assert "llm_evaluation" in d["metadata"]["strategies"]
    assert "concept_coverage" in d["metadata"]["strategies"]


def test_taxonomy_validation():
    p = {
        "question": {
            "id": "bad",
            "text": "x",
            "subject": "science",
            "class_level": "std_5",
            "category": "objective",
            "type": "essay",
        },
        "reference_answer": {"text": "x"},
        "student_answer": {"content": "x", "source": "text"},
    }
    assert client.post("/api/v1/evaluations", json=p).status_code == 422


def test_unit_based_partial_score():
    p = {
        "question": {
            "id": "u1",
            "text": "What is the speed of light?",
            "subject": "science",
            "class_level": "std_8",
            "category": "numerical",
            "type": "unit_based",
            "expected_unit": "m/s"
        },
        "reference_answer": {"text": "300000000 m/s"},
        "student_answer": {"content": "300000000 km/h", "source": "text"}
    }
    d = client.post("/api/v1/evaluations", json=p).json()
    assert d["status"] == "partially_correct"
    assert d["score"] == 50.0
    assert d["error_analysis"]["error_type"] == "unit_error"


def test_formula_normalization():
    p = {
        "question": {
            "id": "f1",
            "text": "Area of a circle?",
            "subject": "mathematics",
            "class_level": "std_8",
            "category": "numerical",
            "type": "formula"
        },
        "reference_answer": {"text": "pi * r^2"},
        "student_answer": {"content": "pi* r²", "source": "text"}
    }
    d = client.post("/api/v1/evaluations", json=p).json()
    assert d["status"] == "correct"
    assert d["score"] == 100.0


def test_graceful_missing_fields_in_rubric():
    # Only 3 required things: text, subject, level, etc., missing expected_concepts and rubric
    p = {
        "question": {
            "id": "g1",
            "text": "Explain gravity.",
            "subject": "science",
            "class_level": "std_5",
            "category": "subjective",
            "type": "explanation"
        },
        "reference_answer": {"text": "Gravity pulls things down."},
        "student_answer": {"content": "It makes things fall to the ground.", "source": "text"}
    }
    r = client.post("/api/v1/evaluations", json=p)
    assert r.status_code == 200
    d = r.json()
    # It should still evaluate successfully utilizing the LLM fallback
    assert d["status"] in ["correct", "partially_correct"]
    assert "llm_evaluation" in d["metadata"]["strategies"]
