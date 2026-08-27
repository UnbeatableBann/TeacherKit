# AI Evaluation Engine V1

Backend-only, text-input educational evaluation engine.

## Locked V1 scope

- Text input only. No OCR, image, handwriting, voice or ASR implementation.
- `StudentAnswer` is separated from evaluation so future input processors can normalize into the same representation.
- Objective, numerical and subjective taxonomy implemented.
- Std 1-12 and UG.
- Mathematics, Science, English, History and General plugins.
- Multiple evaluation strategies per domain/type.
- Structured result with status, score, dimensions, concepts, error analysis, feedback and metadata.

## Dependencies

This project relies on the following key dependencies:
- **FastAPI**: High-performance web framework for the API.
- **Uvicorn**: ASGI web server.
- **Pydantic**: Data validation and strict structured models (v2).
- **Google GenAI**: Client for the LLM evaluation strategy.
- **Scalar FastAPI**: Beautiful interactive API documentation.
- **Pytest**: For running the test suite.
- **Ruff & Mypy**: For linting and static type checking.

## Configuration

The application is configured using environment variables (via `pydantic-settings`). You can create a `.env` file in the root directory. 

Key environment variables:
- `LLM_PROVIDER` (default: `"gemini"`): Set to `"gemini"` to enable real LLM evaluation via Google GenAI.
- `LLM_MODEL` (default: `"gemini-2.5-flash"`): The model used for evaluations.
- `GEMINI_API_KEY`: Your Gemini API key (required if using the Gemini provider).
- `LLM_TIMEOUT` (default: `15`): Timeout in seconds for LLM API calls.

## Setup & Installation

This project uses `uv` for lightning-fast Python package management. 
Ensure you have Python 3.12+ and `uv` installed.

1. Clone the repository and navigate into the root directory.
2. Sync the dependencies and create the virtual environment:
   ```bash
   uv sync
   ```
3. (Optional) Create a `.env` file from the example if you intend to use live LLM features:
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY in the .env file
   ```

## Run Instructions

**Start the Development Server**
```bash
uv run uvicorn app.main:app --reload
```
Once the server is running, you can access the beautiful Scalar API documentation at:
- **API Reference**: [http://127.0.0.1:8000/scalar](http://127.0.0.1:8000/scalar)
- **Standard Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Run Tests**
```bash
uv run pytest
```

**Run Linting & Type Checking**
```bash
uv run ruff check app
uv run ruff format app
uv run mypy app
```

**Production Deployment**
For production, the application is ready to be containerized using the included `Dockerfile`:
```bash
docker build -t ai-evaluation-engine .
docker run -p 8000:8000 --env-file .env ai-evaluation-engine
```

## AI Model Selection

The engine uses **Google GenAI (Gemini 2.5 Flash)** as its primary LLM evaluator (via `LLMStrategy`). 
- **Why Gemini 2.5 Flash?**: It was selected for its blazing-fast inference speed, cost-effectiveness, and large context window. Educational evaluations require near real-time feedback (especially for subjective essay grading), and Gemini 2.5 Flash provides the perfect balance between high-reasoning capability (needed for step-by-step logic, concept extraction, and misconception identification) and extremely low latency compared to heavier reasoning models.

## Known Limitations & Future Improvements

**Known Limitations:**
- **Text-Only Input**: V1 is strictly restricted to text inputs. It currently lacks OCR pipelines for handwritten assignments, image parsing for geometry/diagrams, and ASR for voice inputs.
- **Basic Unit Parsing**: The `UnitBasedStrategy` currently uses simplistic token-splitting to isolate numbers from unit strings. It may struggle with highly complex, non-standard compound units without advanced regex normalization.
- **Rigid Formula Normalization**: Algebraic formula equivalence relies on basic string replacement (e.g. replacing `²` with `^2`) rather than a full Computer Algebra System (CAS).

**Suggested Future Improvements:**
- **SymPy Integration**: Implement a true mathematical solver in the `FormulaStrategy` to correctly assert that algebraically equivalent expressions (e.g., `x(y+z)` and `xy+xz`) match.
- **OCR Pre-processing**: Hook the `StudentAnswer` ingestion pipeline to a vision model (like Gemini 2.5 Pro Vision) or OCR service to support handwritten test papers and diagrams.
- **Async LLM Calls**: Shifting the `LLMStrategy` to use an asynchronous GenAI client (`await evaluator.evaluate_answer(...)`) would drastically improve server throughput and concurrency.
