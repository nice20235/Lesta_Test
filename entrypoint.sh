#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate || { echo "Error: Migrations failed"; exit 1; }

echo "Collecting static files..."
python manage.py collectstatic --noinput || { echo "Error: collectstatic failed"; exit 1; }

echo "Starting uvicorn..."
exec uvicorn combined_asgi:app --host 0.0.0.0 --port 8000
