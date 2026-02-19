FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.0

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --only=main

# Copy application code
COPY . .

# Default: run HTTP server (orchestrator posts jobs here)
# Override with /entrypoint.sh <job_json> for one-shot executor
WORKDIR /app
EXPOSE 8004
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8004"]
