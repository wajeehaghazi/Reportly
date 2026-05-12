# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Create virtual environment and install deps
RUN uv sync --no-dev

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]