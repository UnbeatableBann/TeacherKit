# AI Sales Assistant

## Project Overview
The AI Sales Assistant is a sales representative copilot system designed to process customer conversations, extract requirements, retrieve relevant product recommendations from a vector database (RAG), and generate ready-to-send follow-up messages. It allows a sales representative to paste a customer message or conversation history into the UI and immediately receive actionable intelligence and a drafted response.

## Features

### Implemented
- **Customer Intent & Requirements Extraction**: Parses customer input to identify budget, required features, and objections.
- **Document-Centric Knowledge Base**: Ingests uploaded documents into PostgreSQL (using pgvector), creating embeddings for semantic search.
- **Hybrid RAG Recommendation**: Uses a hybrid vector + keyword retrieval approach to identify matching products or services strictly from the Knowledge Base.
- **Follow-up Generation**: Generates a professional, customer-facing follow-up message incorporating the matched recommendations.
- **Sales Rep UI**: A React-based interface allowing the rep to input customer conversations, view recommendations, and copy the final generated draft.

### Not Implemented
- Voice/Image input.
- Automated email/SMS sending (requires rep intervention).
- Real-time customer chat interface.
- Lead scoring, next-best-action, summary generation, and escalation routing (placeholders exist in UI and schema, but backend returns default stub values in V1).

## Architecture
The system consists of a FastAPI backend and a React/TypeScript frontend.

```
Sales Rep Input (React UI)
       |
   FastAPI (POST /conversations/{id}/messages)
       |
   Service Layer (Follow-up Service & Orchestrator)
       |
 +-----+-----+
 |           |
 LLM      pgvector DB (RAG)
 |           |
 +-----+-----+
       |
 Structured Response (Requirements, Recommendations, Follow-up Draft)
       |
    React UI
```

## Project Structure
```
AI Sales Assistant/
+-- backend/
¦   +-- app/
¦   ¦   +-- api/        # FastAPI route definitions
¦   ¦   +-- models/     # SQLAlchemy database models
¦   ¦   +-- plugins/    # Pipeline stages (analysis, retrieval, generation)
¦   ¦   +-- schemas/    # Pydantic validation schemas
¦   ¦   +-- services/   # Orchestration and business logic
¦   +-- tests/          # Pytest suite
+-- frontend/
¦   +-- src/
¦   ¦   +-- api/        # React Query hooks and API clients
¦   ¦   +-- components/ # React components
¦   ¦   +-- pages/      # View layouts (Dashboard, ConversationView)
¦   ¦   +-- types/      # TypeScript interfaces matching backend schemas
¦   +-- package.json
+-- docker-compose.yml
```

## Technology Stack
**Backend**:
- Python
- FastAPI
- Pydantic v2
- SQLAlchemy
- Google Gemini (via google-genai SDK)
- PostgreSQL + pgvector
- uv, pytest

**Frontend**:
- Node.js
- React
- Vite
- TypeScript
- TailwindCSS

## Prerequisites
- **Python**: 3.12+
- **Node.js**: 20+
- **Database**: PostgreSQL with pgvector extension enabled.
- **Package Managers**: uv (for Python) and npm (for Node).
- **API Key**: A valid Google Gemini API key.

## Dependencies

### Backend
Dependencies are managed via uv using pyproject.toml and uv.lock.
```bash
cd backend
uv sync
```

### Frontend
Dependencies are managed via npm.
```bash
cd frontend
npm install
```

## Configuration

**Backend**: Create backend/.env.
```env
# Required connection string for PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_sales_assistant
# Required Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key
# The model to use (default is gemini-2.5-flash)
MODEL_NAME=gemini-2.5-flash
```

**Frontend**: Create frontend/.env (Optional, defaults to localhost:8000).
```env
VITE_API_URL=http://localhost:8000
```

## Database Setup
1. Ensure PostgreSQL is running.
2. Install the pgvector extension if not already present (CREATE EXTENSION vector;).
3. Create the database (CREATE DATABASE ai_sales_assistant;).
4. Apply migrations using Alembic:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

## Run Instructions

**1. Start Backend**:
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**2. Start Frontend**:
```bash
cd frontend
npm run dev
```

## API Documentation
When the backend is running, Swagger UI is available at http://localhost:8000/docs.

### Important Endpoints:
- POST /conversations/{conversation_id}/messages
  - **Purpose**: Submits a customer message/conversation for analysis and follow-up generation.
  - **Request Body**: {"customer_message": "..."}
  - **Response**: OrchestratorResponse (contains requirements, recommendations, follow_up_message, etc.)

- POST /documents/upload
  - **Purpose**: Uploads a PDF to the Knowledge Base and processes its embeddings.
  - **Request Body**: multipart/form-data

## Example Usage
**Sales Rep Input**:
"I need a software tool for my HR team (approx 100 people) that tracks attendance and syncs with payroll. Budget is 10k/year."

**Backend Processing**:
1. Extracts intent ("Purchase HR software"), requirements (attendance, payroll integration), and budget (10,000).
2. Searches pgvector database for HR software matching these criteria.
3. Formulates a follow-up email recommending matching products and explaining why.

**Output**:
The UI displays the extracted requirements, the specific software recommendations, and an editable follow-up message ready to be copied and sent.

## AI / Model Configuration
The project uses Google Gemini models for both embeddings (text-embedding-004) and generation (gemini-2.5-flash). This is configured in backend/app/services/follow_up_service.py and backend/app/services/document_service.py. The Gemini API requires the GEMINI_API_KEY environment variable. Structured output is strictly enforced using Gemini response_schema parameter combined with Pydantic models.

## RAG / Knowledge Base
- **Ingestion**: PDF documents are parsed using PyMuPDF (fitz).
- **Chunking**: Text is chunked with a predefined token size and overlap.
- **Embedding**: Uses Gemini embedding model.
- **Storage**: Embeddings are stored in PostgreSQL using pgvector.
- **Retrieval**: Performs semantic similarity search, filters based on LLM-extracted requirements, and injects context into the Follow-up Generator prompt.

## Testing
The backend uses pytest and pytest-asyncio.
```bash
cd backend
uv run pytest
```
Testing covers API routes and uses unittest.mock to stub out external LLM API calls and database sessions for deterministic testing.

## Code Quality
Checks can be run via:
```bash
cd backend
uv run ruff check .
```

## Error Handling
- **Database Connection/Vector Issues**: Returns 500 with a relevant HTTP Exception.
- **LLM Quota/Rate Limits**: Catches google.genai.errors.ClientError (429) and returns a specific 429 status instead of a generic 500 error to preserve CORS headers in the frontend.
- **Validation Errors**: Standard FastAPI 422 Unprocessable Entity for invalid schemas.

## Security
- Secrets (GEMINI_API_KEY, DATABASE_URL) are loaded exclusively from .env.
- Database operations use parameterized queries via SQLAlchemy ORM, preventing SQL injection.

## Data Storage
- **Stored**: Uploaded knowledge base documents (metadata and text chunks), extracted customer requirements, generated recommendations, and follow-up drafts.
- **Not Stored**: The physical PDF files are discarded after text extraction.

## Known Limitations
- The system currently only handles PDF documents for the Knowledge Base.
- Lead scoring, next-best-action logic, and escalation endpoints are mocked in V1 (returns 0 or "Not implemented in V1" respectively).
- No multi-tenant isolation or distinct user authentication.
- Follow-up generation assumes text-based email or chat channels.

## Suggested Future Improvements
- Implement accurate lead scoring and escalation routing using historical data.
- Support additional Knowledge Base document types (DOCX, HTML, URLs).
- Enable multi-tenancy and representative login.
- Direct integration with CRM (Salesforce, HubSpot) or email providers via OAuth.

## Troubleshooting
- **CORS Error on POST /messages**: Ensure the backend isn"t crashing with a 500 error due to Gemini quotas (RESOURCE_EXHAUSTED). If this occurs, wait a minute or change to a cheaper model.
- **Missing pgvector**: If migrations fail, ensure you ran CREATE EXTENSION vector; on your Postgres instance.

