"""
Завдання 1: Порівняння асинхронних та синхронних HTTP запитів
"""

import asyncio
import aiohttp
import requests
import time
from typing import List


# ==================== АСИНХРОННА РЕАЛІЗАЦІЯ ====================

async def async_fetch(session: aiohttp.ClientSession, url: str, request_num: int) -> dict:
    """Виконує один асинхронний HTTP GET запит"""
    start = time.time()
    async with session.get(url) as response:
        data = await response.json()
        duration = time.time() - start
        print(f"  Async запит #{request_num} завершено за {duration:.2f}s")
        return data


async def async_http_requests(url: str, num_requests: int = 5) -> None:
    """Виконує кілька HTTP запитів паралельно (асинхронно)"""
    print(f"\n{'='*60}")
    print(f"АСИНХРОННА РЕАЛІЗАЦІЯ ({num_requests} запитів)")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Створюємо список корутин (tasks)
        tasks = [
            async_fetch(session, url, i+1) 
            for i in range(num_requests)
        ]
        
        # Виконуємо всі запити паралельно
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Всі {num_requests} асинхронних запитів виконано")
    print(f"⏱️  Загальний час виконання: {total_time:.2f} секунд")
    print(f"📊 Середній час на запит: {total_time/num_requests:.2f} секунд")
    
    return total_time


# ==================== СИНХРОННА РЕАЛІЗАЦІЯ ====================

def sync_fetch(url: str, request_num: int) -> dict:
    """Виконує один синхронний HTTP GET запит"""
    start = time.time()
    response = requests.get(url)
    data = response.json()
    duration = time.time() - start
    print(f"  Sync запит #{request_num} завершено за {duration:.2f}s")
    return data


def sync_http_requests(url: str, num_requests: int = 5) -> None:
    """Виконує кілька HTTP запитів послідовно (синхронно)"""
    print(f"\n{'='*60}")
    print(f"СИНХРОННА РЕАЛІЗАЦІЯ ({num_requests} запитів)")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    results = []
    for i in range(num_requests):
        result = sync_fetch(url, i+1)
        results.append(result)
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Всі {num_requests} синхронних запитів виконано")
    print(f"⏱️  Загальний час виконання: {total_time:.2f} секунд")
    print(f"📊 Середній час на запит: {total_time/num_requests:.2f} секунд")
    
    return total_time


# ==================== ПОРІВНЯННЯ ====================

def compare_results(async_time: float, sync_time: float, num_requests: int) -> None:
    """Порівнює результати асинхронної та синхронної реалізацій"""
    print(f"\n{'='*60}")
    print("📊 ПОРІВНЯННЯ РЕЗУЛЬТАТІВ")
    print(f"{'='*60}")
    print(f"Кількість запитів: {num_requests}")
    print(f"URL: https://httpbin.org/delay/2 (затримка ~2 секунди)")
    print(f"\n{'Метод':<20} {'Час (сек)':<15} {'Прискорення':<15}")
    print(f"{'-'*50}")
    print(f"{'Асинхронний':<20} {async_time:<15.2f} {'1.00x':<15}")
    print(f"{'Синхронний':<20} {sync_time:<15.2f} {f'{sync_time/async_time:.2f}x':<15}")
    print(f"\n💡 Синхронна версія повільніша в {sync_time/async_time:.2f} разів")
    print(f"\n📝 ПОЯСНЕННЯ:")
    print(f"   • Асинхронна версія: всі запити виконуються паралельно")
    print(f"     - Час ≈ {num_requests} * 0 + 2 сек (затримка сервера) ≈ 2 сек")
    print(f"   • Синхронна версія: запити виконуються послідовно")
    print(f"     - Час ≈ {num_requests} * 2 сек = {num_requests * 2} сек")


# ==================== ГОЛОВНА ФУНКЦІЯ ====================

async def main():
    """Головна функція для запуску тестів"""
    url = "https://httpbin.org/delay/2"
    num_requests = 5
    
    print("\n" + "="*60)
    print("🚀 ТЕСТУВАННЯ HTTP ЗАПИТІВ")
    print("="*60)
    
    # Виконуємо асинхронні запити
    async_time = await async_http_requests(url, num_requests)
    
    # Невелика пауза між тестами
    await asyncio.sleep(1)
    
    # Виконуємо синхронні запити
    sync_time = sync_http_requests(url, num_requests)
    
    # Порівнюємо результати
    compare_results(async_time, sync_time, num_requests)


if __name__ == "__main__":
    # Встановлення необхідних бібліотек:
    # pip install aiohttp requests
    asyncio.run(main())
