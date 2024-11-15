# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./

# Run the build
RUN npm run build

# Stage 2: Final stage
FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/python /app/static /music /config

# Copy Python source code
COPY frontend/python/*.py /app/python/

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist/ /app/static/

# Copy config files
COPY frontend/public/config/ /app/static/config/

# Set essential system environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=11888

# Create gunicorn config file
RUN echo 'import multiprocessing\n\
\n\
# Gunicorn configuration\n\
bind = "0.0.0.0:11888"\n\
workers = multiprocessing.cpu_count() * 2 + 1\n\
worker_class = "gthread"\n\
threads = 4\n\
timeout = 120\n\
keepalive = 5\n\
max_requests = 1000\n\
max_requests_jitter = 50\n\
\n\
# Logging\n\
accesslog = "-"\n\
errorlog = "-"\n\
loglevel = "info"\n\
\n\
# Process naming\n\
proc_name = "trackly"\n\
' > /app/gunicorn.conf.py

# Expose the port
EXPOSE 11888

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

# Set the default command to run gunicorn
CMD ["gunicorn", "--config", "/app/gunicorn.conf.py", "python.wsgi:app"]