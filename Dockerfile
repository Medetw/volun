# ── Stage 1: Build Vue frontend ──────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
ENV VITE_API_BASE_URL=/api
RUN npm run build

# ── Stage 2: Django backend ───────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for psycopg and Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend into Django's expected location
COPY --from=frontend-builder /frontend/dist ./frontend_dist

# Create required directories
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Copy and prepare entrypoint
COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
# 1 worker — укладывается в 512MB RAM (blitz.cloud free tier)
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 120"]
