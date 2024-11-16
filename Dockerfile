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

# Install system dependencies including Nginx
RUN apt-get update && \
    apt-get install -y \
    curl \
    nginx \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/python /app/static /music /data /run/nginx

# Copy Python source code
COPY frontend/python/*.py /app/python/

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist/ /app/static/

# Copy Nginx configuration
COPY config/nginx.conf /etc/nginx/nginx.conf

# Create uwsgi config file
RUN echo '[uwsgi]\n\
socket = /tmp/uwsgi.sock\n\
chown-socket = myuser:myuser\n\
chmod-socket = 664\n\
processes = 4\n\
threads = 2\n\
master = true\n\
vacuum = true\n\
die-on-term = true\n\
module = python.wsgi:app\n\
buffer-size = 32768\n\
harakiri = 120\n\
max-requests = 1000\n\
pythonpath = /app\n\
disable-logging = true\n\
' > /app/uwsgi.ini

# Create entrypoint script
RUN echo '#!/bin/sh\n\
\n\
# Ensure correct permissions\n\
chown -R myuser:myuser /data /app/static\n\
chmod -R 755 /data /app/static\n\
\n\
# Start Nginx\n\
nginx\n\
\n\
# Start uWSGI as myuser\n\
exec su -s /bin/sh myuser -c "uwsgi --ini /app/uwsgi.ini"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set essential system environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=11888

# Expose the port
EXPOSE 11888

# Add Docker metadata
LABEL maintainer="7eventy7"
LABEL version="1.0"
LABEL description="Trackly - Music tracking application"

# Create a non-root user
RUN useradd -m myuser
RUN chown -R myuser:myuser /app /music /data

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11888/ || exit 1

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]