"""
Комплексний скрипт для тестування всіх методів HTTP запитів
Запускає async, sync та multiprocessing і порівнює результати
"""

import asyncio
import aiohttp
import requests
import time
import multiprocessing as mp
from typing import List, Dict


URL = "https://httpbin.org/delay/2"
NUM_REQUESTS = 5


# ==================== АСИНХРОННА РЕАЛІЗАЦІЯ ====================

async def async_fetch(session: aiohttp.ClientSession, url: str, num: int) -> Dict:
    """Виконує асинхронний HTTP запит"""
    start = time.time()
    async with session.get(url) as response:
        await response.json()
        return {'num': num, 'duration': time.time() - start}


async def test_async(url: str, num_requests: int) -> float:
    """Тестує асинхронний підхід"""
    print(f"\n{'='*60}")
    print(f"🔵 ТЕСТ 1: АСИНХРОННИЙ (asyncio + aiohttp)")
    print(f"{'='*60}")
    
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [async_fetch(session, url, i+1) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    duration = time.time() - start
    print(f"✅ Виконано {num_requests} запитів за {duration:.3f}s")
    return duration


# ==================== СИНХРОННА РЕАЛІЗАЦІЯ ====================

def sync_fetch(url: str, num: int) -> Dict:
    """Виконує синхронний HTTP запит"""
    start = time.time()
    requests.get(url)
    return {'num': num, 'duration': time.time() - start}


def test_sync(url: str, num_requests: int) -> float:
    """Тестує синхронний підхід"""
    print(f"\n{'='*60}")
    print(f"🔴 ТЕСТ 2: СИНХРОННИЙ (requests)")
    print(f"{'='*60}")
    
    start = time.time()
    results = [sync_fetch(url, i+1) for i in range(num_requests)]
    duration = time.time() - start
    
    print(f"✅ Виконано {num_requests} запитів за {duration:.3f}s")
    return duration


# ==================== MULTIPROCESSING РЕАЛІЗАЦІЯ ====================

def mp_fetch(args) -> Dict:
    """Виконує HTTP запит в окремому процесі"""
    url, num = args
    start = time.time()
    requests.get(url)
    return {'num': num, 'duration': time.time() - start}


def test_multiprocessing(url: str, num_requests: int) -> float:
    """Тестує multiprocessing підхід"""
    print(f"\n{'='*60}")
    print(f"🟢 ТЕСТ 3: MULTIPROCESSING")
    print(f"{'='*60}")
    
    start = time.time()
    with mp.Pool(processes=num_requests) as pool:
        args_list = [(url, i+1) for i in range(num_requests)]
        results = pool.map(mp_fetch, args_list)
    
    duration = time.time() - start
    print(f"✅ Виконано {num_requests} запитів за {duration:.3f}s")
    return duration


# ==================== ПОРІВНЯННЯ ====================

def print_detailed_comparison(results: Dict[str, float], num_requests: int):
    """Виводить детальне порівняння всіх методів"""
    print(f"\n{'='*70}")
    print(f"📊 ДЕТАЛЬНЕ ПОРІВНЯННЯ ВСІХ МЕТОДІВ")
    print(f"{'='*70}")
    
    # Сортуємо за часом
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    fastest_name, fastest_time = sorted_results[0]
    
    print(f"\n{'Метод':<30} {'Час (сек)':<15} {'Відносна швидкість':<20}")
    print(f"{'-'*70}")
    
    for name, duration in sorted_results:
        if duration == fastest_time:
            relative = "🏆 Найшвидший"
        else:
            slowdown = duration / fastest_time
            relative = f"{slowdown:.2f}x повільніше"
        
        print(f"{name:<30} {duration:<15.3f} {relative:<20}")
    
    # Детальне пояснення
    print(f"\n{'='*70}")
    print(f"📝 ДЕТАЛЬНЕ ПОЯСНЕННЯ")
    print(f"{'='*70}")
    
    async_time = results.get('🔵 Асинхронний (asyncio)', 0)
    sync_time = results.get('🔴 Синхронний (requests)', 0)
    mp_time = results.get('🟢 Multiprocessing', 0)
    
    print(f"\n1️⃣  АСИНХРОННИЙ (asyncio + aiohttp): {async_time:.3f}s")
    print(f"   ╔══════════════════════════════════════════════════════╗")
    print(f"   ║ ✅ ПЕРЕВАГИ:                                         ║")
    print(f"   ║  • Найшвидший для I/O операцій                       ║")
    print(f"   ║  • Мінімальні накладні витрати                       ║")
    print(f"   ║  • Використовує один потік (легкий)                  ║")
    print(f"   ║  • Ефективне використання ресурсів                   ║")
    print(f"   ║                                                       ║")
    print(f"   ║ 🔧 ЯК ПРАЦЮЄ:                                        ║")
    print(f"   ║  1. Event loop керує всіма запитами                  ║")
    print(f"   ║  2. await звільняє управління під час очікування     ║")
    print(f"   ║  3. Всі {num_requests} запитів виконуються паралельно           ║")
    print(f"   ║  4. Час ≈ час одного запиту (~2s)                    ║")
    print(f"   ╚══════════════════════════════════════════════════════╝")
    
    print(f"\n2️⃣  СИНХРОННИЙ (requests): {sync_time:.3f}s")
    print(f"   ╔══════════════════════════════════════════════════════╗")
    print(f"   ║ ❌ НЕДОЛІКИ:                                         ║")
    print(f"   ║  • Найповільніший метод                              ║")
    print(f"   ║  • Блокує виконання на кожному запиті                ║")
    print(f"   ║  • Неефективне використання ресурсів                 ║")
    print(f"   ║  • Погана масштабованість                            ║")
    print(f"   ║                                                       ║")
    print(f"   ║ 🔧 ЯК ПРАЦЮЄ:                                        ║")
    print(f"   ║  1. Виконує запити один за одним                     ║")
    print(f"   ║  2. Кожен запит блокує виконання                     ║")
    print(f"   ║  3. Потрібно чекати завершення кожного               ║")
    print(f"   ║  4. Час ≈ {num_requests} × 2s = {num_requests * 2}s                           ║")
    print(f"   ╚══════════════════════════════════════════════════════╝")
    
    print(f"\n3️⃣  MULTIPROCESSING: {mp_time:.3f}s")
    print(f"   ╔══════════════════════════════════════════════════════╗")
    print(f"   ║ ⚠️  ХАРАКТЕРИСТИКИ:                                  ║")
    print(f"   ║  • Швидкий, але з накладними витратами               ║")
    print(f"   ║  • Створює {num_requests} окремих процесів Python              ║")
    print(f"   ║  • Кожен процес має власний GIL і пам'ять            ║")
    print(f"   ║  • Великі накладні витрати на створення процесів     ║")
    print(f"   ║                                                       ║")
    print(f"   ║ 🔧 ЯК ПРАЦЮЄ:                                        ║")
    print(f"   ║  1. Створює пул з {num_requests} процесів                       ║")
    print(f"   ║  2. Кожен процес виконує свій запит                  ║")
    print(f"   ║  3. Справжній паралелізм (окремі CPU cores)          ║")
    print(f"   ║  4. Час ≈ час запиту + overhead (~0.3-0.5s)          ║")
    print(f"   ╚══════════════════════════════════════════════════════╝")
    
    # Рекомендації
    print(f"\n{'='*70}")
    print(f"💡 РЕКОМЕНДАЦІЇ ПО ВИКОРИСТАННЮ")
    print(f"{'='*70}")
    
    print(f"\n📌 Використовуйте ASYNCIO коли:")
    print(f"   ✅ Робота з HTTP API (requests, webhooks)")
    print(f"   ✅ Робота з базами даних (PostgreSQL, MongoDB)")
    print(f"   ✅ Читання/запис файлів")
    print(f"   ✅ WebSockets, SSE")
    print(f"   ✅ Будь-які I/O операції з очікуванням")
    print(f"   ")
    print(f"   💰 Економія ресурсів: 1 потік може обробити тисячі запитів!")
    
    print(f"\n📌 Використовуйте MULTIPROCESSING коли:")
    print(f"   ✅ CPU-інтенсивні обчислення (ML, data processing)")
    print(f"   ✅ Паралельна обробка великих датасетів")
    print(f"   ✅ Математичні розрахунки")
    print(f"   ✅ Обхід GIL (Global Interpreter Lock)")
    print(f"   ")
    print(f"   ⚠️  Для I/O операцій - надмірно! Використовуйте asyncio.")
    
    print(f"\n📌 УНИКАЙТЕ синхронного коду коли:")
    print(f"   ❌ Потрібно обробити багато I/O операцій")
    print(f"   ❌ Розробляєте сервер або API")
    print(f"   ❌ Час виконання критичний")
    print(f"   ")
    print(f"   ✅ Синхронний код OK тільки для простих скриптів")
    
    # Графічне порівняння часу
    print(f"\n{'='*70}")
    print(f"📊 ВІЗУАЛІЗАЦІЯ ЧАСУ ВИКОНАННЯ")
    print(f"{'='*70}\n")
    
    max_time = max(results.values())
    bar_width = 50
    
    for name, duration in sorted_results:
        bar_length = int((duration / max_time) * bar_width)
        bar = '█' * bar_length
        print(f"{name:<30} {bar} {duration:.3f}s")
    
    print(f"\n{'='*70}")


# ==================== ГОЛОВНА ФУНКЦІЯ ====================

async def main():
    """Головна функція"""
    print("\n" + "="*70)
    print("🚀 КОМПЛЕКСНЕ ТЕСТУВАННЯ МЕТОДІВ HTTP ЗАПИТІВ")
    print("="*70)
    print(f"\n📋 Параметри тестування:")
    print(f"   • URL: {URL}")
    print(f"   • Кількість запитів: {NUM_REQUESTS}")
    print(f"   • Затримка на сервері: ~2 секунди")
    print(f"   • Методи: Asyncio, Sync, Multiprocessing")
    
    results = {}
    
    # Тест 1: Асинхронний
    try:
        async_time = await test_async(URL, NUM_REQUESTS)
        results['🔵 Асинхронний (asyncio)'] = async_time
    except Exception as e:
        print(f"❌ Помилка в асинхронному тесті: {e}")
    
    # Пауза між тестами
    print("\n⏸️  Пауза 2 секунди...")
    await asyncio.sleep(2)
    
    # Тест 2: Синхронний
    try:
        sync_time = test_sync(URL, NUM_REQUESTS)
        results['🔴 Синхронний (requests)'] = sync_time
    except Exception as e:
        print(f"❌ Помилка в синхронному тесті: {e}")
    
    # Пауза між тестами
    print("\n⏸️  Пауза 2 секунди...")
    await asyncio.sleep(2)
    
    # Тест 3: Multiprocessing
    try:
        mp_time = test_multiprocessing(URL, NUM_REQUESTS)
        results['🟢 Multiprocessing'] = mp_time
    except Exception as e:
        print(f"❌ Помилка в multiprocessing тесті: {e}")
    
    # Виводимо порівняння
    if results:
        print_detailed_comparison(results, NUM_REQUESTS)
    
    print(f"\n{'='*70}")
    print("✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Необхідно для Windows
    mp.freeze_support()
    
    # Запускаємо тести
    asyncio.run(main())
