.PHONY: run-evaluator evaluator-backend evaluator-frontend run-generator generator-backend generator-frontend run-sales sales-backend sales-frontend

run-evaluator:
	@echo "Starting AI Question Evaluator..."
	$(MAKE) -j2 evaluator-backend evaluator-frontend

evaluator-backend:
	cd "AI Question Evaluator" && uv run uvicorn app.main:app --port 8000 --reload

evaluator-frontend:
	cd "AI Question Evaluator/frontend" && npm run dev -- --port 5173

run-generator:
	@echo "Starting AI Question Generator..."
	@docker start pgvector 2>nul || echo "Note: pgvector docker container might not be running or is already up."
	$(MAKE) -j2 generator-backend generator-frontend

generator-backend:
	cd "AI Question Generator" && uv run uvicorn app.main:app --port 8002 --reload

generator-frontend:
	cd "AI Question Generator/frontend" && npm run dev -- --port 5174

run-sales:
	@echo "Starting AI Sales Assistant..."
	$(MAKE) -j2 sales-backend sales-frontend

sales-backend:
	cd "AI Sales Assistant/backend" && uv run uvicorn app.main:app --port 8001 --reload

sales-frontend:
	cd "AI Sales Assistant/frontend" && npm run dev -- --port 5175
