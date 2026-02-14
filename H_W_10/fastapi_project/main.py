"""
Домашнє завдання — Частина 2: FastAPI сервер
Два ендпоінти: /blocking (time.sleep) vs /non-blocking (asyncio.sleep)
+ PostgreSQL через SQLAlchemy (async) для логування запитів
"""

import time
import asyncio
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, Integer
import os

# ─────────────────────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://fastapi_user:fastapi_password@db:5432/fastapi_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class RequestLog(Base):
    """Модель для логування запитів."""
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint: Mapped[str] = mapped_column(String(50))
    duration: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# APP INITIALIZATION
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Blocking vs Non-Blocking Demo",
    description="Демонстрація різниці між блокуючим та неблокуючим sleep у FastAPI",
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    """Створення таблиць при старті."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency для отримання сесії БД."""
    async with AsyncSessionLocal() as session:
        yield session


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    return {
        "message": "FastAPI Blocking vs Non-Blocking Demo",
        "endpoints": {
            "/blocking":     "Блокуючий sleep (time.sleep) — зависає весь event loop",
            "/non-blocking": "Неблокуючий sleep (asyncio.sleep) — event loop вільний",
            "/logs":         "Логи всіх запитів з БД",
            "/explain":      "Пояснення різниці",
        }
    }


@app.get("/blocking", tags=["Demo"])
async def blocking_endpoint(db: AsyncSession = Depends(get_db)):
    """
    ⛔ БЛОКУЮЧИЙ endpoint.

    time.sleep(2) БЛОКУЄ весь Python thread, в якому крутиться event loop.
    Поки один запит 'спить', інші паралельні запити до цього ендпоінта
    вишиковуються в чергу і чекають.

    При 5 паралельних запитах: загальний час ≈ 5 × 2 = 10 секунд
    (у режимі одного воркера Uvicorn).
    """
    start = time.perf_counter()

    # ⛔ Блокує весь event loop!
    time.sleep(2)

    duration = time.perf_counter() - start

    # Логуємо в БД
    log = RequestLog(endpoint="blocking", duration=duration)
    db.add(log)
    await db.commit()

    return JSONResponse({
        "endpoint": "blocking",
        "sleep_type": "time.sleep(2)  ← блокує весь event loop",
        "duration_sec": round(duration, 3),
        "warning": "⛔ Цей запит заблокував thread на 2 сек. "
                   "Інші запити чекали в черзі!"
    })


@app.get("/non-blocking", tags=["Demo"])
async def non_blocking_endpoint(db: AsyncSession = Depends(get_db)):
    """
    ✅ НЕБЛОКУЮЧИЙ endpoint.

    await asyncio.sleep(2) ПОВЕРТАЄ контроль event loop-у.
    Поки 'спимо', event loop обробляє інші корутини.
    Усі 5 паралельних запитів стартують одночасно і завершуються ~разом.

    При 5 паралельних запитах: загальний час ≈ 2 секунди.
    """
    start = time.perf_counter()

    # ✅ Відпускає event loop — інші корутини можуть виконуватись
    await asyncio.sleep(2)

    duration = time.perf_counter() - start

    # Логуємо в БД
    log = RequestLog(endpoint="non-blocking", duration=duration)
    db.add(log)
    await db.commit()

    return JSONResponse({
        "endpoint": "non-blocking",
        "sleep_type": "asyncio.sleep(2)  ← event loop вільний",
        "duration_sec": round(duration, 3),
        "info": "✅ Поки цей запит 'спав', event loop обслуговував інші запити!"
    })


@app.get("/logs", tags=["Stats"])
async def get_logs(db: AsyncSession = Depends(get_db)):
    """Отримати логи всіх запитів з БД."""
    from sqlalchemy import select
    result = await db.execute(
        select(RequestLog).order_by(RequestLog.created_at.desc()).limit(50)
    )
    logs = result.scalars().all()
    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "endpoint": log.endpoint,
                "duration_sec": round(log.duration, 3),
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
    }


@app.get("/explain", tags=["Info"])
async def explain():
    """Детальне пояснення різниці."""
    return {
        "title": "Blocking vs Non-Blocking у FastAPI / ASGI",
        "event_loop": {
            "description": "FastAPI використовує asyncio event loop — однопотоковий цикл подій.",
            "blocking": "time.sleep() заморожує ВЕСЬ потік. Event loop стоїть. Нічого не виконується.",
            "non_blocking": "asyncio.sleep() каже event loop: 'я почекаю, займись іншими'. Loop продовжує роботу.",
        },
        "thread_blocking": {
            "time_sleep": "Блокує OS-потік → uvicorn worker не може обробляти нові запити.",
            "asyncio_sleep": "Не блокує потік → worker обробляє десятки запитів одночасно.",
        },
        "concurrency": {
            "blocking_5_requests":     "5 × 2 сек = ~10 сек (послідовно в 1 воркері)",
            "non_blocking_5_requests": "max(2, 2, 2, 2, 2) = ~2 сек (справжній конкурентний I/O)",
        },
        "analogy": (
            "Уявіть кухаря (event loop). time.sleep — він стоїть і дивиться на таймер, "
            "нічого не роблячи. asyncio.sleep — він поставив таймер і пішов готувати "
            "наступну страву. Через 2 хв повернувся до першої."
        ),
        "rule": "Завжди використовуй async/await для I/O в FastAPI. "
                "Sync блокуючий код → run_in_executor або окремий worker!",
    }
