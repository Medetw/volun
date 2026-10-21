#!/bin/bash
set -e

# Wait for PostgreSQL
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL..."
    while ! python -c "
import urllib.parse, socket
parsed = urllib.parse.urlparse('$DATABASE_URL')
s = socket.socket()
try:
    s.connect((parsed.hostname, parsed.port or 5432))
    s.close()
except:
    exit(1)
" 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up"

    # Create database if it doesn't exist
    python -c "
import urllib.parse, psycopg
parsed = urllib.parse.urlparse('$DATABASE_URL')
db_name = (parsed.path or '').lstrip('/')
conn = psycopg.connect(
    host=parsed.hostname, port=parsed.port or 5432,
    user=parsed.username, password=parsed.password,
    dbname='postgres', autocommit=True
)
try:
    conn.execute(f'CREATE DATABASE \"{db_name}\"')
    print(f'Database {db_name} created')
except psycopg.errors.DuplicateDatabase:
    print(f'Database {db_name} already exists')
conn.close()
"
fi

# Run migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser from environment variables if provided (blitz.cloud env vars)
# Uses DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ] || [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser from DJANGO_SUPERUSER_* environment variables..."
    python manage.py createsuperuser --noinput || true
fi

# Create test accounts (idempotent — safe to run on every restart)
if [ "${DJANGO_CREATE_TEST_ACCOUNTS:-1}" = "1" ]; then
    echo "Creating test accounts..."
    python manage.py create_test_accounts
fi

# Start server
exec "$@"
