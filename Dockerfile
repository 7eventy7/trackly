# Stage 1: Build frontend
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Build backend and combine with frontend
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/src/ ./src/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# Create necessary directories
RUN mkdir -p /music /config

# Set essential system environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHON_PATH=/app

# Add Docker metadata
LABEL maintainer="7eventy7"
LABEL version="1.0"
LABEL description="Trackly - Music tracking application"

# Create a non-root user and switch to it
RUN useradd -m myuser
RUN chown -R myuser:myuser /app /music /config
USER myuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11888/ || exit 1

# Set the default command
CMD ["python", "src/main.py"]