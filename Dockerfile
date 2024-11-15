# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./

# Run the build
RUN npm run build

# Stage 2: Build backend and combine with frontend
FROM python:3.12-slim AS final

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

# Copy Python source code from the correct location
COPY frontend/python/ ./python/

# Copy built frontend from previous stage to the correct location
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# Copy config files to the correct location
COPY frontend/public/config/ ./static/config/

# Create necessary directories
RUN mkdir -p /music /config

# Set essential system environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHON_PATH=/app
ENV PORT=11888

# Create a Flask application file
RUN echo 'from flask import Flask, send_from_directory\n\
import os\n\
from python.main import main as tracker_main\n\
import threading\n\
\n\
def create_app():\n\
    app = Flask(__name__, static_folder="static")\n\
\n\
    @app.route("/")\n\
    def serve_index():\n\
        return send_from_directory(app.static_folder, "index.html")\n\
\n\
    @app.route("/config/<path:filename>")\n\
    def serve_config(filename):\n\
        return send_from_directory(os.path.join(app.static_folder, "config"), filename)\n\
\n\
    @app.route("/<path:path>")\n\
    def serve_static(path):\n\
        return send_from_directory(app.static_folder, path)\n\
\n\
    # Start the tracker in a separate thread\n\
    tracker_thread = threading.Thread(target=tracker_main, daemon=True)\n\
    tracker_thread.start()\n\
\n\
    return app\n\
\n\
app = create_app()\n\
\n\
if __name__ == "__main__":\n\
    app.run()\n\
' > ./server.py

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
\n\
# SSL (uncomment if using HTTPS)\n\
# keyfile = "/etc/certs/key.pem"\n\
# certfile = "/etc/certs/cert.pem"\n\
' > ./gunicorn.conf.py

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
CMD ["gunicorn", "--config", "gunicorn.conf.py", "server:app"]