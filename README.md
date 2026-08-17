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
- **OpenAI**: Client for the LLM evaluation strategy.
- **Scalar FastAPI**: Beautiful interactive API documentation.
- **Pytest**: For running the test suite.
- **Ruff & Mypy**: For linting and static type checking.

## Configuration

The application is configured using environment variables (via `pydantic-settings`). You can create a `.env` file in the root directory. 

Key environment variables:
- `LLM_PROVIDER` (default: `"mock"`): Set to `"openai"` to enable real LLM evaluation.
- `LLM_MODEL` (default: `"gpt-4o-mini"`): The model used for evaluations.
- `LLM_API_KEY`: Your OpenAI API key (required if using the OpenAI provider).
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
   # Add your OPENAI_API_KEY in the .env file
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
