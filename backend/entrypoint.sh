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

# Start server
exec "$@"
