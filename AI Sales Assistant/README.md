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

## Setup

### Backend
1. Ensure PostgreSQL is running with the `pgvector` extension installed.
2. Configure `.env` in `backend/` using `.env.example`.
3. `cd backend`
4. Install dependencies via pip or pipenv.
5. Apply Alembic migrations or run `python scripts/seed.py` for initial setup.
6. Run server: `uvicorn app.main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Core Requirements Satisfied
- [x] Identify customer intent and requirements.
- [x] Recommend products strictly from the catalogue.
- [x] Explain recommendations based on catalogue data.
- [x] Grounding Validator strictly enforces facts without hallucination.
- [x] Generate professional follow-up messages.
- [x] React Dashboard for Sales Rep with SSE simulated UI layout.
