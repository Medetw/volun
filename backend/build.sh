#!/usr/bin/env bash
# exit on error
set -o errexit

# Create directories needed by Django
mkdir -p logs

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
