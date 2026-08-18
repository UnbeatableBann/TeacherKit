# TeacherKit Monorepo

Welcome to the **TeacherKit** monorepo! This repository contains a suite of AI-powered applications designed to streamline educational content creation, student evaluation, and administrative workflows. 

Each project operates as its own independent service and contains its own respective configuration, databases, and dependencies.

## Projects

### 1. [AI Question Generator](./AI%20Question%20Generator/)
A production-ready platform that analyzes previous-year examination papers (via PDF) and generates **brand new**, structurally equivalent questions.
- **Backend Engine**: FastAPI, Pydantic v2.
- **AI Core**: Google Gemini 2.5 Pro for structural extraction, deep taxonomy analysis, and RAG-infused question generation.
- **Database**: PostgreSQL with `pgvector` for semantic similarity mapping and avoiding duplicate generation.
- **Workflow**: Documents → Extraction → Concept Analysis → Deterministic Generation Planner → Semantic Context Retrieval → LLM Generation → Scheme Validation.

### 2. [AI Sales Assistant](./AI%20Sales%20Assistant/)
A full-stack intelligent agent and dashboard tailored to automate engagement, catalogue lookups, and administrative responses.
- **Backend Engine**: FastAPI, PostgreSQL, and Google Gemini SDK.
- **Frontend Dashboard**: React + Vite (TypeScript).
- **Features**: Agentic workflow for lead scoring, conversational requirement extraction, intent recognition, RAG against CSV catalogues, objection handling, and automatic escalation bounding.

### 3. [AI Question Evaluator](./AI%20Question%20Evaluator/)
*(Documentation coming soon)* - A component designed to algorithmically and semantically evaluate the quality, difficulty, and validity of educational questions.

---

## Global Setup

Ensure you have the following installed locally on your system to work with this monorepo effectively:

1. **Python 3.12+**
2. **Node.js 20+** (for frontend applications)
3. **[uv](https://github.com/astral-sh/uv)** (Python package & environment manager)
4. **PostgreSQL** (with the `pgvector` extension installed)

## Environment Configuration
Each individual project folder contains its own `.env.example` file. To run a project locally, duplicate the `.env.example` to `.env` inside its respective folder and populate it with your local database credentials and your **Google Gemini API Key**.

*(For detailed setup and execution instructions, please refer to the `README.md` located inside each specific project folder).*
