"""
Клієнтський скрипт для тестування blocking vs non-blocking ендпоінтів
"""

import asyncio
import aiohttp
import time
from datetime import datetime
from typing import List, Tuple


async def fetch_endpoint(
    session: aiohttp.ClientSession, 
    url: str, 
    request_num: int,
    endpoint_type: str
) -> dict:
    """Виконує один запит до ендпоінту"""
    start = time.time()
    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    emoji = "🔴" if endpoint_type == "blocking" else "🟢"
    print(f"{emoji} [{current_time}] Відправка запиту #{request_num} до /{endpoint_type}")
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            data = await response.json()
            duration = time.time() - start
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            print(f"{emoji} [{current_time}] Відповідь #{request_num} отримана за {duration:.3f}s")
            
            return {
                'request_num': request_num,
                'duration': duration,
                'success': True,
                'data': data
            }
    except Exception as e:
        duration = time.time() - start
        print(f"❌ Запит #{request_num} помилка: {e}")
        return {
            'request_num': request_num,
            'duration': duration,
            'success': False,
            'error': str(e)
        }


async def test_endpoint(
    base_url: str, 
    endpoint: str, 
    num_requests: int = 5
) -> Tuple[float, List[dict]]:
    """
    Тестує один ендпоінт, роблячи num_requests паралельних запитів
    
    Returns:
        Tuple[загальний час, список результатів]
    """
    endpoint_type = "blocking" if "blocking" in endpoint else "non-blocking"
    emoji = "🔴" if endpoint_type == "blocking" else "🟢"
    
    print(f"\n{'='*60}")
    print(f"{emoji} ТЕСТУВАННЯ /{endpoint_type.upper()} ({num_requests} паралельних запитів)")
    print(f"{'='*60}")
    
    url = f"{base_url}/{endpoint}"
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Створюємо задачі для паралельного виконання
        tasks = [
            fetch_endpoint(session, url, i+1, endpoint_type)
            for i in range(num_requests)
        ]
        
        # Виконуємо всі запити паралельно
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # Аналізуємо результати
    successful = sum(1 for r in results if r.get('success'))
    durations = [r['duration'] for r in results if r.get('success')]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    print(f"\n{emoji} ===== РЕЗУЛЬТАТИ для /{endpoint_type} =====")
    print(f"⏱️  Загальний час: {total_time:.3f} секунд")
    print(f"✅ Успішних запитів: {successful}/{num_requests}")
    print(f"📊 Середній час відповіді: {avg_duration:.3f} секунд")
    
    return total_time, results


def print_comparison(blocking_time: float, non_blocking_time: float, num_requests: int):
    """Виводить детальне порівняння результатів"""
    print(f"\n{'='*60}")
    print("📊 ДЕТАЛЬНЕ ПОРІВНЯННЯ РЕЗУЛЬТАТІВ")
    print(f"{'='*60}")
    
    print(f"\n{'Ендпоінт':<20} {'Час (сек)':<15} {'Різниця':<20}")
    print(f"{'-'*55}")
    print(f"{'🟢 /non-blocking':<20} {non_blocking_time:<15.3f} {'(базовий)':<20}")
    print(f"{'🔴 /blocking':<20} {blocking_time:<15.3f} {f'(+{blocking_time - non_blocking_time:.3f}s)':<20}")
    
    slowdown = blocking_time / non_blocking_time if non_blocking_time > 0 else 0
    print(f"\n💡 Blocking повільніший у {slowdown:.2f} разів")
    
    print(f"\n{'='*60}")
    print("📝 ПОЯСНЕННЯ РІЗНИЦІ")
    print(f"{'='*60}")
    
    print(f"\n🟢 NON-BLOCKING endpoint (/non-blocking):")
    print(f"   Час виконання: ~{non_blocking_time:.3f}s")
    print(f"   ")
    print(f"   Як працює:")
    print(f"   1. Використовує await asyncio.sleep(2)")
    print(f"   2. Коли викликається await, event loop ЗВІЛЬНЯЄТЬСЯ")
    print(f"   3. Event loop може обробляти ІНШІ запити")
    print(f"   4. Всі {num_requests} запитів обробляються ПАРАЛЕЛЬНО")
    print(f"   ")
    print(f"   Часова діаграма:")
    print(f"   Request 1: |--sleep(2)--|")
    print(f"   Request 2: |--sleep(2)--|")
    print(f"   Request 3: |--sleep(2)--|  <- Всі виконуються ОДНОЧАСНО")
    print(f"   Request 4: |--sleep(2)--|")
    print(f"   Request 5: |--sleep(2)--|")
    print(f"   Total:     |----~2s----|")
    print(f"   ")
    print(f"   ✅ Результат: ~2 секунди (час одного sleep)")
    
    print(f"\n🔴 BLOCKING endpoint (/blocking):")
    print(f"   Час виконання: ~{blocking_time:.3f}s")
    print(f"   ")
    print(f"   Як працює:")
    print(f"   1. Використовує time.sleep(2)")
    print(f"   2. time.sleep() БЛОКУЄ весь потік виконання")
    print(f"   3. Event loop НЕ МОЖЕ обробляти інші запити")
    print(f"   4. Запити обробляються ПОСЛІДОВНО (один за одним)")
    print(f"   ")
    print(f"   Часова діаграма:")
    print(f"   Request 1: |--sleep(2)--|")
    print(f"   Request 2:                |--sleep(2)--|")
    print(f"   Request 3:                               |--sleep(2)--|  <- ПОСЛІДОВНО")
    print(f"   Request 4:                                              |--sleep(2)--|")
    print(f"   Request 5:                                                             |--sleep(2)--|")
    print(f"   Total:     |----~{num_requests * 2}s----|")
    print(f"   ")
    print(f"   ❌ Результат: ~{num_requests * 2} секунд ({num_requests} × 2 секунди)")
    
    print(f"\n{'='*60}")
    print("🔍 ТЕХНІЧНІ ДЕТАЛІ")
    print(f"{'='*60}")
    
    print(f"\n1️⃣  EVENT LOOP:")
    print(f"   • FastAPI працює на ASGI сервері (uvicorn)")
    print(f"   • Використовує asyncio event loop")
    print(f"   • Event loop = цикл обробки подій (запитів)")
    print(f"   ")
    print(f"   NON-BLOCKING:")
    print(f"   - await asyncio.sleep() повертає управління event loop")
    print(f"   - Event loop обробляє інші запити під час очікування")
    print(f"   ")
    print(f"   BLOCKING:")
    print(f"   - time.sleep() БЛОКУЄ весь потік Python")
    print(f"   - Event loop НЕ МОЖЕ робити нічого під час sleep")
    
    print(f"\n2️⃣  БЛОКУВАННЯ ПОТОКУ:")
    print(f"   • Python використовує один потік для event loop")
    print(f"   • time.sleep() блокує цей потік → event loop зупиняється")
    print(f"   • await asyncio.sleep() НЕ блокує → event loop працює")
    
    print(f"\n3️⃣  КОНКУРЕНТНІСТЬ В FASTAPI:")
    print(f"   • FastAPI дозволяє async та sync функції")
    print(f"   • async def → виконується в event loop (конкурентно)")
    print(f"   • def → виконується в thread pool (блокує якщо є time.sleep)")
    print(f"   ")
    print(f"   NON-BLOCKING (async def):")
    print(f"   - Запити обробляються конкурентно в одному потоці")
    print(f"   - Переключення між запитами через await")
    print(f"   ")
    print(f"   BLOCKING (def):")
    print(f"   - FastAPI запускає в окремому потоці")
    print(f"   - Але time.sleep() все одно блокує цей потік")
    print(f"   - Кількість одночасних запитів обмежена thread pool")
    
    print(f"\n{'='*60}")
    print("💡 ВИСНОВКИ")
    print(f"{'='*60}")
    print(f"✅ ВИКОРИСТОВУЙТЕ non-blocking (await asyncio.sleep):")
    print(f"   • Для I/O операцій (HTTP, БД, файли)")
    print(f"   • Максимальна конкурентність")
    print(f"   • Ефективне використання ресурсів")
    print(f"")
    print(f"❌ УНИКАЙТЕ blocking (time.sleep):")
    print(f"   • Блокує обробку інших запитів")
    print(f"   • Погана масштабованість")
    print(f"   • Якщо потрібен blocking код → використовуйте run_in_executor()")


async def main():
    """Головна функція"""
    base_url = "http://localhost:8000"
    num_requests = 5
    
    print("\n" + "="*60)
    print("🚀 КЛІЄНТСЬКЕ ТЕСТУВАННЯ FASTAPI СЕРВЕРА")
    print("="*60)
    print(f"\n📌 Сервер: {base_url}")
    print(f"📌 Кількість паралельних запитів: {num_requests}")
    print(f"📌 Очікувана затримка кожного запиту: 2 секунди")
    
    try:
        # Перевіряємо доступність сервера
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    print(f"\n❌ Сервер недоступний на {base_url}")
                    print("   Переконайтесь, що server.py запущений!")
                    return
        
        print(f"✅ Сервер доступний\n")
        
        # Невелика затримка перед початком
        await asyncio.sleep(1)
        
        # Тестуємо blocking ендпоінт
        blocking_time, blocking_results = await test_endpoint(
            base_url, "blocking", num_requests
        )
        
        # Пауза між тестами
        print(f"\n{'='*60}")
        print("⏸️  Пауза 3 секунди перед наступним тестом...")
        print(f"{'='*60}")
        await asyncio.sleep(3)
        
        # Тестуємо non-blocking ендпоінт
        non_blocking_time, non_blocking_results = await test_endpoint(
            base_url, "non-blocking", num_requests
        )
        
        # Виводимо порівняння
        print_comparison(blocking_time, non_blocking_time, num_requests)
        
    except aiohttp.ClientConnectorError:
        print(f"\n❌ Не вдалося підключитися до сервера на {base_url}")
        print("   ")
        print("   Для запуску сервера виконайте в іншому терміналі:")
        print("   python server.py")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Встановлення необхідних бібліотек:
    # pip install aiohttp
    asyncio.run(main())
