FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./

RUN npm run build

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    curl \
    nginx \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/python /app/static /music /data /run/nginx

COPY frontend/python/*.py /app/python/

COPY --from=frontend-builder /app/frontend/dist/ /app/static/

COPY config/nginx.conf /etc/nginx/nginx.conf

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

RUN echo '#!/bin/sh\n\
\n\
chown -R myuser:myuser /data /app/static\n\
chmod -R 755 /data /app/static\n\
\n\
nginx\n\
\n\
exec su -s /bin/sh myuser -c "uwsgi --ini /app/uwsgi.ini"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=11888

EXPOSE 11888

LABEL maintainer="7eventy7"
LABEL version="1.0"
LABEL description="Trackly - Music tracking application"

RUN useradd -m myuser
RUN chown -R myuser:myuser /app /music /data

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11888/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]