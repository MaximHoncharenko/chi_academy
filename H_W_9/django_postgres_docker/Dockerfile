# Використовуємо офіційний Python образ
FROM python:3.11-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements.txt
COPY requirements.txt /app/

# Встановлюємо Python залежності
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проєкт
COPY . /app/

# Створюємо директорію для статичних файлів
RUN mkdir -p /app/staticfiles

# Відкриваємо порт 8000
EXPOSE 8000

# Скрипт запуску
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Запускаємо entrypoint скрипт
ENTRYPOINT ["/app/entrypoint.sh"]
