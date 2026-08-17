FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install uv for fast dependency resolution and installation
RUN pip install --no-cache-dir uv==0.5.2

# Copy pyproject.toml and lockfile
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync
RUN uv sync --no-dev --frozen

# Copy application source code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Start Uvicorn server in production mode
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
