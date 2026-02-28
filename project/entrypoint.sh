#!/bin/sh
set -e

echo '=== Stamping Alembic (schema created by init.sql) ==='
alembic stamp head

echo '=== Seeding database ==='
python scripts/seed.py

echo '=== Starting API server ==='
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
