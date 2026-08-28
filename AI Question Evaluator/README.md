# AI Question Evaluator

## Project Overview
The AI Question Evaluator is a backend-only educational evaluation engine. It processes student answers in text format, compares them against a provided question and rubric, and outputs a structured evaluation result including score, error analysis, feedback, and identified concepts. It is designed for educational platforms needing automated grading for objective, numerical, and subjective questions across Mathematics, Science, English, and History (Std 1-12 and UG).

## Features

### Implemented
- Text-based evaluation of student answers.
- Exact match, numerical, and formula-based evaluation strategies (without LLMs).
- LLM-based evaluation strategy for subjective answers (using Gemini).
- Domain-specific plugins (Mathematics, Science, English, History, General).
- Extraction of score, dimensions, concepts, error analysis, and feedback.

### Not Implemented
- Image, OCR, or handwriting input.
- Voice/ASR input.
- Complex algebraic equivalence checking (e.g. CAS solver).

## Architecture
The system is built as a FastAPI service using a strategy pattern for evaluation.

```
Request (Question + Answer)
       |
    FastAPI
       |
 Plugin Registry -> Selects Domain Plugin
       |
 Evaluation Strategy (Exact, Numerical, Formula, LLM)
       |
 Structured Evaluation Result
       |
    FastAPI
```

## Project Structure
```
app/
+-- api/          # FastAPI endpoints
+-- core/         # Settings and configuration
+-- models/       # Core domain models (Question, Answer, Result)
+-- plugins/      # Domain-specific logic (math, science, etc.)
+-- strategies/   # Evaluation algorithms (LLM, Exact Match, etc.)
+-- main.py       # FastAPI application entry point
```

## Technology Stack
- **Backend:** Python, FastAPI, Pydantic v2
- **AI:** Google GenAI SDK (Gemini)
- **Tooling:** uv, Ruff, Mypy, Pytest

## Prerequisites
- **Python**: >=3.12
- **Package Manager**: uv
- **API Key**: Google Gemini API Key

## Dependencies
Dependencies are managed using uv (pyproject.toml and uv.lock).
```bash
uv sync
```

## Configuration
Configure using `.env`.
```env
# Required for LLM evaluation
GEMINI_API_KEY=your_gemini_api_key
# The LLM provider (default: gemini)
LLM_PROVIDER=gemini
# The model used (default: gemini-2.5-flash)
LLM_MODEL=gemini-2.5-flash
# Timeout for LLM calls (default: 15)
LLM_TIMEOUT=15
```

## Run Instructions
```bash
uv run uvicorn app.main:app --reload
```

## API Documentation
Once running, view the interactive Scalar API documentation at `http://127.0.0.1:8000/scalar` (or standard Swagger at `/docs`).

### Important Endpoints
- POST `/api/v1/evaluate`
  - **Purpose**: Evaluates a student answer.
  - **Request Body**: `EvaluationRequest` (Question, StudentAnswer, Context)
  - **Response**: `EvaluationResult` (Score, feedback, error analysis)

## Example Usage
**Input**:
```json
{
  "question": {"text": "What is the capital of France?", "type": "subjective", "domain": "general"},
  "answer": {"text": "I think it is Paris."}
}
```
**Output**:
```json
{
  "status": "success",
  "score": 1.0,
  "feedback": "Correct! Paris is the capital of France.",
  "concepts": ["Geography", "Capitals"]
}
```

## AI / Model Configuration
Uses `gemini-2.5-flash` via Google GenAI for its fast inference speed and cost-effectiveness. Structured output is enforced using Pydantic schemas passed to the SDK.

## Testing
Tests cover unit, integration, and mocked LLM components.
```bash
uv run pytest
```

## Code Quality
```bash
uv run ruff check app
uv run ruff format app
uv run mypy app
```

## Error Handling
- Validates input strictly via Pydantic.
- LLM timeouts are handled gracefully, returning evaluation failure status without crashing the server.

## Data Storage
- **Stored**: Nothing is persisted. This is a stateless processing engine.
- **Not Stored**: Evaluation requests and results are not saved to any database.

## Known Limitations
- Strictly limited to text input. No OCR or diagram parsing.
- Formula equivalence relies on basic string replacement rather than a Computer Algebra System.
- Basic unit parsing relies on simple token splitting.

## Suggested Future Improvements
- Integrate SymPy for true mathematical formula equivalence checking.
- Hook into OCR/Vision models for handwritten diagram support.
- Refactor LLM calls to use asynchronous clients for higher throughput.

