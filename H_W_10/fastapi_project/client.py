"""
Домашнє завдання — Клієнтський скрипт
Робить 5 паралельних запитів до /blocking та /non-blocking,
вимірює час і пояснює різницю.
"""

import asyncio
import time
import httpx

BASE_URL = "http://localhost:8000"
NUM_REQUESTS = 5


# ─────────────────────────────────────────────────────────────
# ASYNC клієнт: паралельні запити через httpx + asyncio.gather
# ─────────────────────────────────────────────────────────────
async def make_request(
    client: httpx.AsyncClient,
    url: str,
    request_num: int
) -> dict:
    """Один асинхронний запит з вимірюванням часу."""
    start = time.perf_counter()
    response = await client.get(url, timeout=60)
    elapsed = time.perf_counter() - start

    data = response.json()
    print(f"    запит #{request_num} → статус {response.status_code} "
          f"| {elapsed:.2f}s | {data.get('sleep_type', '')}")
    return {"num": request_num, "status": response.status_code, "elapsed": elapsed}


async def benchmark_endpoint(endpoint: str, label: str) -> float:
    """5 паралельних запитів до ендпоінта, повертає загальний час."""
    url = f"{BASE_URL}/{endpoint}"
    print(f"\n{'='*60}")
    print(f"  🔍 Тестуємо /{endpoint} ({label})")
    print(f"     {NUM_REQUESTS} паралельних запитів → {url}")
    print(f"{'='*60}")

    async with httpx.AsyncClient() as client:
        wall_start = time.perf_counter()

        # Запускаємо всі 5 запитів ОДНОЧАСНО
        tasks = [
            make_request(client, url, i)
            for i in range(1, NUM_REQUESTS + 1)
        ]
        results = await asyncio.gather(*tasks)

        total_elapsed = time.perf_counter() - wall_start

    individual_times = [r["elapsed"] for r in results]
    print(f"\n  Індивідуальний час запитів: "
          f"{[f'{t:.2f}s' for t in individual_times]}")
    print(f"  ⏱  Загальний час (wall-clock): {total_elapsed:.2f} сек")
    return total_elapsed


async def run_benchmark():
    # Перевіряємо доступність сервера
    print("\n" + "="*60)
    print("  🚀 КЛІЄНТСЬКИЙ БЕНЧМАРК: blocking vs non-blocking")
    print("="*60)

    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{BASE_URL}/", timeout=5)
        print(f"  ✅ Сервер доступний на {BASE_URL}")
    except httpx.ConnectError:
        print(f"\n  ❌ Сервер недоступний на {BASE_URL}")
        print("  Запустіть спочатку: uvicorn main:app --reload")
        print("  або: docker-compose up")
        return

    # ── ТЕСТ 1: BLOCKING ──────────────────────────────────────
    t_blocking = await benchmark_endpoint("blocking", "time.sleep(2)")

    # Пауза між тестами
    print("\n  ⏳ Пауза 1 секунда між тестами...")
    await asyncio.sleep(1)

    # ── ТЕСТ 2: NON-BLOCKING ─────────────────────────────────
    t_non_blocking = await benchmark_endpoint("non-blocking", "asyncio.sleep(2)")

    # ── ПІДСУМОК ──────────────────────────────────────────────
    print_summary(t_blocking, t_non_blocking)


def print_summary(t_blocking: float, t_non_blocking: float):
    speedup = t_blocking / t_non_blocking if t_non_blocking > 0 else float("inf")

    print("\n" + "="*60)
    print("  📊 ПІДСУМОК ПОРІВНЯННЯ")
    print("="*60)
    print(f"  /blocking     (time.sleep):    {t_blocking:>7.2f} сек  ⛔")
    print(f"  /non-blocking (asyncio.sleep): {t_non_blocking:>7.2f} сек  ✅")
    print(f"  Пришвидшення: x{speedup:.1f}  "
          f"({'non-blocking швидше! 🚀' if speedup > 1 else 'щось пішло не так'})")
    print()

    print("  🔍 ПОЯСНЕННЯ РІЗНИЦІ:")
    print()
    print("  1️⃣  EVENT LOOP:")
    print("      • time.sleep(2) — ЗУПИНЯЄ event loop на 2 сек.")
    print("        Жодна інша корутина не може виконатись.")
    print("      • asyncio.sleep(2) — ВІДПУСКАЄ event loop.")
    print("        Він продовжує обробляти інші запити.")
    print()
    print("  2️⃣  БЛОКУВАННЯ ПОТОКУ:")
    print("      • time.sleep → блокує OS-потік (WSGI-стиль).")
    print("        5 запитів × 2 сек = 10 сек послідовно.")
    print("      • asyncio.sleep → не блокує потік (ASGI-стиль).")
    print("        5 запитів стартують разом → ~2 сек загалом.")
    print()
    print("  3️⃣  КОНКУРЕНТНІСТЬ у FastAPI / ASGI:")
    print("      • FastAPI → Uvicorn (ASGI сервер) → asyncio event loop.")
    print("      • Один воркер може обробляти тисячі concurrent запитів —")
    print("        АЛЕ тільки якщо код async і не блокує loop!")
    print("      • Sync/blocking код → запуск через run_in_executor")
    print("        (thread pool), щоб не заморожувати loop.")
    print()
    print("  💡 ЗОЛОТЕ ПРАВИЛО FastAPI:")
    print("      async def + await = ✅  (I/O не блокує)")
    print("      def + time.sleep  = ⚠️   (блокує весь сервер!)")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
