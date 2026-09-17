#!/usr/bin/env bash
# Railway build script — runs from repo root
set -o errexit

echo "==> Installing Node.js dependencies..."
cd frontend
npm install

echo "==> Building Vue frontend..."
npm run build
cd ..

echo "==> Copying frontend dist into Django..."
rm -rf backend/frontend_dist
cp -r frontend/dist backend/frontend_dist

echo "==> Installing Python dependencies..."
cd backend
mkdir -p logs
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Build complete!"
