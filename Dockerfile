# Multi-stage Dockerfile for CEE Pipeline
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.docker.txt requirements.txt
COPY requirements.txt requirements.base.txt

# Install Python dependencies (use Docker-specific requirements with PostgreSQL)
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True)"

# Copy application code
COPY . .

# Make init script executable
RUN chmod +x docker-init.sh

# Create directories
RUN mkdir -p /app/data /app/logs

# Expose port for API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Use init script as entrypoint
ENTRYPOINT ["/app/docker-init.sh"]

# Default command
CMD ["uvicorn", "cee_pipeline.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
