# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ .

# Environment variables (will be overridden by docker-compose.yml)
ENV MUSIC_PATH=/music \
    UPDATE_INTERVAL="0 * * * *" \
    DISCORD_WEBHOOK=""

# Run the script
CMD ["python", "main.py"]