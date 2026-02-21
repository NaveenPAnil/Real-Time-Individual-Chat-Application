#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (if env vars provided)
python manage.py shell < create_superuser.py

# Collect static files
python manage.py collectstatic --no-input
