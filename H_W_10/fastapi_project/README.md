# 🚀 FastAPI: Blocking vs Non-Blocking + Docker + PostgreSQL

## 📁 Структура проєкту

```
fastapi_project/
├── main.py                  # FastAPI сервер (blocking & non-blocking ендпоінти)
├── client.py                # Клієнт: 5 паралельних запитів + бенчмарк
├── part1_http_requests.py   # Частина 1: sync vs async vs multiprocessing
├── Dockerfile               # Образ FastAPI
├── docker-compose.yml       # FastAPI + PostgreSQL
├── entrypoint.sh            # Очікування PostgreSQL + запуск uvicorn
├── requirements.txt         # Залежності
└── .env                     # Змінні середовища
```

---

## ⚡ Швидкий старт

### Варіант 1 — Docker (рекомендовано)

```bash
docker-compose up --build
```

Відкрийте:
- **API docs**: http://localhost:8000/docs
- **Пояснення**: http://localhost:8000/explain
- **Логи запитів**: http://localhost:8000/logs

Запустіть клієнт (в іншому терміналі):
```bash
docker-compose exec web python client.py
```

### Варіант 2 — Локально

```bash
pip install -r requirements.txt
uvicorn main:app --reload        # термінал 1
python client.py                 # термінал 2
python part1_http_requests.py    # термінал 3 (потрібен інтернет)
```

---

## 📌 Частина 1 — sync vs async vs multiprocessing

**Файл:** `part1_http_requests.py`

```bash
python part1_http_requests.py
```

### Очікувані результати:

| Підхід          | Час (5 запитів × 2 сек) | Пояснення                              |
|-----------------|------------------------|----------------------------------------|
| Синхронний      | ~10 сек                | Запити йдуть один за одним             |
| Asyncio         | ~2 сек                 | Усі 5 стартують паралельно             |
| Multiprocessing | ~3–5 сек               | Паралельно, але + накладні на процеси  |

### Чому asyncio найшвидше для I/O?

```
Синхронно:   [req1────][req2────][req3────][req4────][req5────]  ~10s
Asyncio:     [req1────]
              [req2────]
              [req3────]
              [req4────]
              [req5────]
             ──────────── ~2s (усі разом)
Multiproc:   [proc1──][req1────]
              [proc2──][req2────]   + час на fork процесів
             ──────────── ~3-5s
```

---

## 🔀 Частина 2 — FastAPI: /blocking vs /non-blocking

### Ендпоінти:

| URL             | Реалізація              | 5 паралельних запитів |
|-----------------|-------------------------|-----------------------|
| `/blocking`     | `time.sleep(2)`         | ~10 сек ⛔            |
| `/non-blocking` | `await asyncio.sleep(2)`| ~2 сек  ✅            |

### Клієнт (benchmark):

```bash
python client.py
```

Приклад виводу:
```
============================================================
  🔍 Тестуємо /blocking (time.sleep(2))
============================================================
    запит #1 → статус 200 | 2.01s
    запит #2 → статус 200 | 4.02s
    запит #3 → статус 200 | 6.03s
    запит #4 → статус 200 | 8.04s
    запит #5 → статус 200 | 10.05s
  ⏱  Загальний час: 10.05 сек

============================================================
  🔍 Тестуємо /non-blocking (asyncio.sleep(2))
============================================================
    запит #1 → статус 200 | 2.01s
    запит #2 → статус 200 | 2.01s
    запит #3 → статус 200 | 2.01s
    запит #4 → статус 200 | 2.01s
    запит #5 → статус 200 | 2.01s
  ⏱  Загальний час: 2.01 сек
```

---

## 🧠 Пояснення різниці

### 1️⃣ Event Loop

```
FastAPI → Uvicorn (ASGI) → asyncio event loop

time.sleep(2):        asyncio.sleep(2):
┌──────────────┐      ┌──────────────┐
│ event loop   │      │ event loop   │
│   FROZEN ❌  │      │   FREE ✅    │
│              │      │   handles    │
│  no other    │      │   req2, req3 │
│  tasks run   │      │   req4, req5 │
└──────────────┘      └──────────────┘
```

### 2️⃣ Блокування потоку

```python
# ⛔ ПОГАНО — блокує весь OS thread:
@app.get("/bad")
async def bad():
    time.sleep(2)        # ЗУПИНЯЄ event loop!
    return {"ok": True}

# ✅ ДОБРЕ — відпускає event loop:
@app.get("/good")
async def good():
    await asyncio.sleep(2)   # loop продовжує роботу
    return {"ok": True}

# ✅ ДОБРЕ — sync код у thread pool:
@app.get("/sync-ok")
async def sync_ok():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, time.sleep, 2)  # у окремому thread
    return {"ok": True}
```

### 3️⃣ Конкурентність у FastAPI / ASGI

```
ASGI (FastAPI + Uvicorn):
  1 worker = 1 event loop = тисячі concurrent запитів
  (якщо весь код async і не блокує!)

WSGI (Flask/Django + Gunicorn):
  1 worker = 1 запит одночасно
  Потрібно N workers для N паралельних запитів

Blocking у ASGI = найгірший сценарій:
  1 worker + time.sleep(2) + 5 запитів = 10 сек
  (немов WSGI, але без переваг!)
```

---

## 🐳 Docker

### Dockerfile пояснення:

```dockerfile
FROM python:3.11-slim           # Легкий базовий образ

ENV PYTHONDONTWRITEBYTECODE=1   # Без .pyc файлів
ENV PYTHONUNBUFFERED=1          # Логи одразу в stdout

WORKDIR /app

RUN apt-get install libpq-dev   # Для psycopg2

COPY requirements.txt .
RUN pip install -r requirements.txt   # Окремий шар → кешується

COPY . .                        # Копіюємо код

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]   # Чекає PostgreSQL
```

### docker-compose.yml пояснення:

```yaml
services:
  db:                           # PostgreSQL
    image: postgres:15-alpine   # Легкий Alpine образ
    healthcheck:                # Перевірка готовності
      test: pg_isready ...
      
  web:                          # FastAPI
    build: .                    # Збираємо з Dockerfile
    depends_on:
      db:
        condition: service_healthy   # Чекаємо healthy БД!
    environment:
      DATABASE_URL: postgresql+asyncpg://...
```

### Важливо: `service_healthy` vs `service_started`

```yaml
# ❌ НЕ ДОСТАТНЬО — сервіс запущений, але DB може не відповідати
depends_on:
  db:
    condition: service_started

# ✅ ПРАВИЛЬНО — чекаємо поки PostgreSQL справді готовий
depends_on:
  db:
    condition: service_healthy
```

---

## 🗄️ База даних (PostgreSQL)

FastAPI логує кожен запит до таблиці `request_logs`:

```sql
SELECT * FROM request_logs ORDER BY created_at DESC LIMIT 10;
```

Перегляд через API: http://localhost:8000/logs

### Підключення до PostgreSQL:

```bash
# Через docker-compose
docker-compose exec db psql -U fastapi_user -d fastapi_db

# Напряму (порт 5432 відкритий)
psql -h localhost -U fastapi_user -d fastapi_db
```

---

## 🔧 Корисні команди

```bash
# Запуск
docker-compose up --build

# Фоновий режим
docker-compose up -d --build

# Логи
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f db

# Клієнтський бенчмарк
docker-compose exec web python client.py

# Частина 1 (потрібен інтернет для httpbin.org)
docker-compose exec web python part1_http_requests.py

# PostgreSQL shell
docker-compose exec db psql -U fastapi_user -d fastapi_db

# Зупинити
docker-compose down

# Зупинити + видалити дані
docker-compose down -v
```

---

## 📊 Підсумок — золоті правила

| Ситуація                    | Рішення                                         |
|-----------------------------|-------------------------------------------------|
| Async I/O (HTTP, DB, файли) | `async def` + `await`                           |
| Sync бібліотека             | `asyncio.run_in_executor(None, sync_func)`      |
| CPU-intensive               | `multiprocessing` або `ProcessPoolExecutor`     |
| Паралельні I/O запити       | `asyncio.gather(*tasks)`                        |
| Блокуючий sleep в тестах    | `await asyncio.sleep()` замість `time.sleep()`  |

---

## 💡 Висновок

> FastAPI + asyncio дозволяє одному воркеру обробляти тисячі
> concurrent запитів — але ТІЛЬКИ якщо код не блокує event loop.
> `time.sleep()` в async функції = антипатерн, який вбиває
> всю перевагу асинхронного підходу.
