# AI Question Generator from Previous-Year Examination Papers

## System Overview
This is a production-ready software system designed to analyze previous-year examination papers (PDFs), understand their structure and patterns, and generate genuinely new questions following those patterns without copying them.

## Features
- **Document Ingestion:** Background processing of uploaded previous-year papers (supports only PDF format).
- **Structured Extraction:** Uses PyMuPDF and LLMs to parse text and extract questions via structured schemas.
- **Question Analysis:** Analyzes extracted questions to classify Topic, Concepts, and Difficulty using Google Gemini LLM.
- **Deterministic Generation Planning:** Builds a generation distribution (e.g., matching the original difficulty and topic spread).
- **Retrieval Augmented Generation (RAG):** Fetches historical question context from the vector database matching the planned topic and difficulty.
- **Question Generation:** Uses gemini-2.5-pro to create new, historically-aligned questions.
- **Validation & Deduplication:** Verifies question parameters (like marks) and uses pgvector similarity search to ensure newly generated questions are not duplicates of historical ones.

## Architecture
- **API & Core:** FastAPI, Pydantic v2. Background tasks for asynchronous processing.
- **API Documentation:** Uses Scalar instead of standard Swagger UI (accessible at /scalar).
- **Database:** PostgreSQL with the pgvector extension for vector similarity searches, interfaced via SQLAlchemy and asyncpg. Migrations managed by alembic.
- **LLM Engine:** Google GenAI SDK using gemini-2.5-pro for structured extraction, analysis, and generation.
- **Data flow:**
  1. Document Upload (PDF) via API.
  2. Background task triggers text extraction via PyMuPDF.
  3. Question extraction via structured LLM schema.
  4. Question analysis (Topic, Concepts, Difficulty) via structured LLM.
  5. Generation Request -> Deterministic Planner builds a question distribution.
  6. RAG -> Fetches historical context matching the planned topic & difficulty.
  7. Generator -> Uses Gemini to create new questions adhering to historical style.
  8. Validator -> Verifies marks, ensures no duplicates using vector search.

## Dependencies
- **Python:** >= 3.14 (as defined in pyproject.toml). Managed via uv.
- **Database:** PostgreSQL with pgvector extension installed.
- **API Keys:** Google Gemini API Key.
- **Core Packages:** fastapi, pydantic v2, sqlalchemy, asyncpg, pymupdf, google-genai, alembic, scalar-fastapi.

## Configuration
Configure the application using environment variables. Create a .env file:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_question_generator
VECTOR_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_question_generator
GEMINI_API_KEY=your_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-pro
```

## Setup
1. Clone the repository.
2. Ensure you have uv installed.
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Start your PostgreSQL database and ensure the pgvector extension is created.
5. Run migrations:
   ```bash
   uv run alembic upgrade head
   ```

## Testing
The project uses pytest and pytest-asyncio for testing, structured into unit and integration test suites.
- Run tests using `uv run pytest`.
- The test suite heavily utilizes unittest.mock to stub out the database (SQLAlchemy sessions) and LLM responses (Google GenAI SDK) for isolated testing of components like the GenerationPlanner, QuestionAnalyzer, and QuestionValidator.

## Code Quality
Checks can be run via:
```bash
uv run ruff check .
```

## Data Storage
- **Stored**: Uploaded examination papers (metadata and text chunks), extracted questions, generated questions.
- **Not Stored**: Original PDF binary files are discarded after processing.

## Limitations & Known Issues
- **Speed & Performance:** Uploading and generation speed currently require optimization. Processing can take time due to multiple LLM calls per document.
- **File Support:** Currently hardcoded to only accept .pdf files.
- **Python Versioning:** pyproject.toml strictly requires Python >=3.14, which may pose compatibility issues with current stable environments.
- **UI Responsiveness:** UI integration needs improvement to better handle the asynchronous nature of the background processing APIs.

## Suggested Future Improvements
- Persistent job queue (e.g. Celery or RedisQ) for background processing instead of standard FastAPI BackgroundTasks.
- Support for images and docx files.
- Authentication/authorization.
- Additional LLM providers (OpenAI, Anthropic).
- Horizontal scaling.

## Run Instructions
Run the FastAPI development server:
```bash
uv run uvicorn app.main:app --reload
```
Access the interactive API docs at http://localhost:8000/scalar.

