# TeacherKit Monorepo

## Repository Overview
This repository contains a suite of independent, AI-powered applications designed for educational content creation, student evaluation, and administrative workflows. 

Each project operates as its own independent service and contains its own respective configuration, databases, and dependencies.

## Projects

### 1. [AI Question Generator](./AI%20Question%20Generator/)
A backend system that analyzes previous-year examination papers (PDFs), extracts their structure and concepts, and generates new questions that match the historical difficulty and topic distribution.
- **Technologies**: Python, FastAPI, PostgreSQL, pgvector, Google Gemini.
- **Status**: Backend API implemented. Requires PostgreSQL with pgvector.

### 2. [AI Sales Assistant](./AI%20Sales%20Assistant/)
A full-stack copilot system for sales representatives. It processes customer conversations, retrieves product recommendations from an uploaded Knowledge Base (RAG), and generates drafted follow-up messages.
- **Technologies**: Python, FastAPI, React, Node.js, PostgreSQL, pgvector, Google Gemini.
- **Status**: Full-stack application implemented. Requires PostgreSQL with pgvector.

### 3. [AI Question Evaluator](./AI%20Question%20Evaluator/)
A stateless backend evaluation engine that grades student text answers against rubrics using Exact Match, Numerical, and LLM-based strategies across multiple educational domains.
- **Technologies**: Python, FastAPI, Google Gemini.
- **Status**: Backend API implemented. No database required.

## High-Level Setup
To run the projects in this repository, you generally need:
- **Python >=3.12** (managed via `uv`)
- **Node.js 20+** (for frontend applications)
- **PostgreSQL** (with `pgvector` extension for the Database-backed apps)
- **Google Gemini API Key**

Each project is independent. Please navigate to the specific project directory and read its `README.md` for detailed instructions on dependencies, environment variables, database migrations, and run commands.

