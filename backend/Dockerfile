FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.docker

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    netcat-openbsd \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs

# Create non-root user
RUN groupadd -r django && useradd -r -g django django && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ || exit 1

# Run migrations, collect static, and start server
CMD ["sh", "-c", "
    python manage.py migrate &&
    python manage.py collectstatic --noinput &&
    python manage.py create_initial_data &&
    gunicorn --bind 0.0.0.0:8000 --workers 3 --worker-class sync --worker-tmp-dir /dev/shm --max-requests 1000 --max-requests-jitter 100 --timeout 30 --keep-alive 2 config.wsgi:application
"]
