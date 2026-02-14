#!/bin/bash
set -e

echo "──────────────────────────────────────────────"
echo "  🐍 FastAPI — запуск контейнера"
echo "──────────────────────────────────────────────"

# ── Чекаємо, поки PostgreSQL стане доступним ──────
echo "⏳ Чекаємо на PostgreSQL ($DB_HOST:$DB_PORT)..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "   PostgreSQL ще не готовий — спробуємо через 1 сек..."
  sleep 1
done

echo "✅ PostgreSQL готовий!"

# ── Запускаємо Uvicorn ────────────────────────────
echo ""
echo "🚀 Стартуємо Uvicorn на 0.0.0.0:8000"
echo "──────────────────────────────────────────────"

exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
