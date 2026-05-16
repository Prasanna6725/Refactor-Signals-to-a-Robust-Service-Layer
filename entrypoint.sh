#!/usr/bin/env bash
set -e

# Run migrations
python manage.py migrate --noinput

# Create superuser if variables exist
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi

echo "Starting command: $@"

exec "$@"