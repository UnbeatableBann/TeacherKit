# AI Question Generator from Previous-Year Examination Papers

## System Overview
This is a production-ready software system designed to analyze previous-year examination papers (PDFs), understand their structure and patterns, and generate genuinely new questions following those patterns without copying them.

## Architecture
- **API & Core**: FastAPI, Pydantic v2.
- **Database**: PostgreSQL with `pgvector` for vector similarity searches, using SQLAlchemy and `asyncpg`.
- **LLM Engine**: Google GenAI SDK using `gemini-2.5-pro` (by default) for structed extraction, analysis, and generation.
- **Data flow**:
  1. Document Upload (PDF).
  2. Text extraction via PyMuPDF.
  3. Question extraction via structured LLM schema.
  4. Question analysis (Topic, Concepts, Difficulty) via structured LLM.
  5. Generation Request -> deterministic planner builds a distribution.
  6. RAG -> fetches historical context matching the planned topic & difficulty.
  7. Generator -> uses Gemini to create new questions adhering to historical style.
  8. Validator -> verifies marks, ensures no duplicates.

## Setup & Requirements
### Prerequisites
- Python 3.12+ (managed via `uv`).
- PostgreSQL with `pgvector` extension installed.
- Google Gemini API Key.

### Installation
1. Clone the repository.
2. Ensure you have `uv` installed.
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Set up `.env` based on `.env.example`.
5. Run migrations (requires running DB):
   ```bash
   uv run alembic upgrade head
   ```

### Running Locally
```bash
uv run uvicorn app.main:app --reload
```
Access the API docs at `http://localhost:8000/docs`.
