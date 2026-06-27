#!/usr/bin/env bash
# exit on error
set -o errexit

# Create directories needed by Django
mkdir -p logs

# 1. Build the Vue frontend
echo "==> Building frontend..."
cd ../frontend
npm install
npm run build
cd ../backend

# 2. Copy frontend dist into Django
echo "==> Copying frontend build to Django..."
rm -rf frontend_dist
cp -r ../frontend/dist frontend_dist

# 3. Install Python dependencies
echo "==> Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Collect static files (includes frontend assets)
echo "==> Collecting static files..."
python manage.py collectstatic --no-input

# 5. Run database migrations
echo "==> Running migrations..."
python manage.py migrate
