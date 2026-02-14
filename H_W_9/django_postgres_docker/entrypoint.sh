#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."

# Очікування доступності PostgreSQL
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - continuing..."

# Застосування міграцій
echo "Applying database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Завантаження фікстур (якщо потрібно)
echo "Loading fixtures..."
python manage.py loaddata library/fixtures/initial_data.json || true

# Збір статичних файлів
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Створення суперкористувача (тільки якщо не існує)
echo "Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
END

echo "Starting server..."
# Запуск сервера
exec python manage.py runserver 0.0.0.0:8000
