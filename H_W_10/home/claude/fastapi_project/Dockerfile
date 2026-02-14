# ─────────────────────────────────────────────────
# Dockerfile для FastAPI застосунку
# Базовий образ: python:3.11-slim (легкий, немає зайвих пакетів)
# ─────────────────────────────────────────────────

FROM python:3.11-slim

# Не генерувати .pyc файли і не буферизувати stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Робоча директорія всередині контейнера
WORKDIR /app

# ── Системні залежності ───────────────────────────
# libpq-dev потрібен для psycopg2
# gcc — для компіляції деяких Python пакетів
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python залежності ─────────────────────────────
# Копіюємо тільки requirements спочатку → кешування шарів Docker
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Копіюємо весь проєкт ──────────────────────────
COPY . .

# ── Entrypoint скрипт ─────────────────────────────
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Порт, на якому слухає Uvicorn
EXPOSE 8000

# Запуск через entrypoint (чекає PostgreSQL, потім стартує)
ENTRYPOINT ["/app/entrypoint.sh"]
