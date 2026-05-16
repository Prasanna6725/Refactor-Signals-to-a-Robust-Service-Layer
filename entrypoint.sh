#!/usr/bin/env bash
set -e

# Run migrations then start dev server
python manage.py migrate --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi

echo "Starting Django development server"
python manage.py runserver 0.0.0.0:8000
