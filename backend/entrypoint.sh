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
fi

# Run migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
exec "$@"
