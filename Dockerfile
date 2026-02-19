# Multi-stage Dockerfile for production deployment
# Builds React frontend and FastAPI backend in a single optimized image

# ============================================================================
# Stage 1: Build React Frontend
# ============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies (using npm ci for faster, reliable builds)
RUN npm ci --only=production --ignore-scripts && \
    npm ci --only=development --ignore-scripts || \
    (npm install --legacy-peer-deps && npm cache clean --force)

# Copy frontend source
COPY frontend/ .

# Build React app for production
RUN npm run build

# ============================================================================
# Stage 2: Python Base Image
# ============================================================================
FROM python:3.11-slim AS python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 3: Python Dependencies
# ============================================================================
FROM python-base AS python-deps

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 4: Production Image
# ============================================================================
FROM python-base AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python dependencies from deps stage
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy React build from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Render will set PORT environment variable)
EXPOSE 8000

# Health check (uses PORT env var, defaults to 8000)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c "python -c \"import urllib.request, os; port = os.environ.get('PORT', '8000'); urllib.request.urlopen(f'http://localhost:{port}/health')\"" || exit 1

# Default command (can be overridden by Render)
# Uses PORT environment variable if set, otherwise defaults to 8000
CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"

