# Backend Dockerfile for EssayMentor AI
# Django + Celery + Channels

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy project files
COPY backend/ /app/backend/
COPY agents/ /app/agents/
COPY vector_db/ /app/vector_db/
COPY university_profiles.json /app/
COPY data/ /app/data/

# Create directory for ChromaDB
RUN mkdir -p /app/chroma_db

# Expose port
EXPOSE 8000

# Default command - can be overridden in docker-compose
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.essaymentor.asgi:application"]
