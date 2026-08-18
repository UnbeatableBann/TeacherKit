# AI Sales Assistant

A full-stack production-ready AI Sales Assistant with a plugin-based orchestration engine.

## Architecture

The backend is built with FastAPI and PostgreSQL (using pgvector), structured around a central Orchestrator that invokes isolated Plugins reading from a shared SessionState. This ensures the recommendation pipeline, RAG grounding, objection handling, and scoring are decoupled and independently testable.

### Plugins Implemented:
1. Intent & Requirement Extraction
2. Catalogue Retrieval (pgvector semantic search + exact matching filters)
3. Recommendation
4. Grounding Validator (Strips LLM hallucinations from catalogue records)
5. Objection Handling
6. QA
7. Lead Scoring
8. Next-Best-Action
9. Conversation Summary
10. Follow-Up Generator
11. Escalation

## Dependencies
**Backend:**
- Python 3.12+ 
- PostgreSQL with `pgvector`
- FastAPI, SQLAlchemy, `google-genai` SDK

**Frontend:**
- Node.js 20+
- React, Vite, TypeScript, TailwindCSS

## Configuration
Configure the application using environment variables.

**Backend Configuration:**
Create a `.env` file in the `backend/` directory (use `.env.example` as a template):
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db?ssl=require
JWT_SECRET=super_secret_jwt_key_123
GEMINI_API_KEY=your_gemini_api_key
```

**Frontend Configuration:**
Create a `.env` file in the `frontend/` directory (if needed):
```env
VITE_API_URL=http://localhost:8000
```

## Setup
### Backend
1. Ensure PostgreSQL is running with the `pgvector` extension installed.
2. `cd backend`
3. Install dependencies via pip or pipenv.
4. Apply Alembic migrations or run `python scripts/seed.py` for initial setup.

### Frontend
1. `cd frontend`
2. `npm install`

## Run Instructions
**Run Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Run Frontend:**
```bash
cd frontend
npm run dev
```

## Core Requirements Satisfied
- [x] Identify customer intent and requirements.
- [x] Recommend products strictly from the catalogue.
- [x] Explain recommendations based on catalogue data.
- [x] Grounding Validator strictly enforces facts without hallucination.
- [x] Generate professional follow-up messages.
- [x] React Dashboard for Sales Rep with SSE simulated UI layout.
