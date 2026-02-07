"""
Завдання 1*: Реалізація через multiprocessing
"""

import multiprocessing as mp
import requests
import time
from typing import List


def fetch_with_process(args) -> dict:
    """
    Функція для виконання HTTP запиту в окремому процесі
    Args - кортеж (url, request_num)
    """
    url, request_num = args
    start = time.time()
    
    try:
        response = requests.get(url)
        data = response.json()
        duration = time.time() - start
        print(f"  Process #{request_num} (PID: {mp.current_process().pid}) завершено за {duration:.2f}s")
        return {
            'request_num': request_num,
            'duration': duration,
            'success': True,
            'data': data
        }
    except Exception as e:
        duration = time.time() - start
        print(f"  Process #{request_num} помилка: {e}")
        return {
            'request_num': request_num,
            'duration': duration,
            'success': False,
            'error': str(e)
        }


def multiprocessing_http_requests(url: str, num_requests: int = 5) -> float:
    """Виконує HTTP запити використовуючи multiprocessing"""
    print(f"\n{'='*60}")
    print(f"MULTIPROCESSING РЕАЛІЗАЦІЯ ({num_requests} запитів)")
    print(f"{'='*60}")
    print(f"Головний процес PID: {mp.current_process().pid}")
    
    start_time = time.time()
    
    # Створюємо пул процесів
    with mp.Pool(processes=num_requests) as pool:
        # Готуємо аргументи для кожного запиту
        args_list = [(url, i+1) for i in range(num_requests)]
        
        # Виконуємо запити паралельно в різних процесах
        results = pool.map(fetch_with_process, args_list)
    
    total_time = time.time() - start_time
    
    # Аналізуємо результати
    successful = sum(1 for r in results if r.get('success'))
    
    print(f"\n✅ Всі {num_requests} запитів через multiprocessing виконано")
    print(f"⏱️  Загальний час виконання: {total_time:.2f} секунд")
    print(f"📊 Успішних запитів: {successful}/{num_requests}")
    print(f"📊 Середній час на запит: {total_time/num_requests:.2f} секунд")
    
    return total_time


def compare_all_methods(async_time: float, sync_time: float, mp_time: float, num_requests: int):
    """Порівнює всі три методи"""
    print(f"\n{'='*60}")
    print("📊 ПОРІВНЯННЯ ВСІХ МЕТОДІВ")
    print(f"{'='*60}")
    print(f"Кількість запитів: {num_requests}")
    print(f"\n{'Метод':<25} {'Час (сек)':<15} {'Прискорення':<15}")
    print(f"{'-'*55}")
    
    times = [
        ("Асинхронний (asyncio)", async_time),
        ("Синхронний (послідовний)", sync_time),
        ("Multiprocessing", mp_time)
    ]
    
    # Сортуємо за часом
    times.sort(key=lambda x: x[1])
    fastest_time = times[0][1]
    
    for method, t in times:
        speedup = f"{fastest_time/t:.2f}x" if t == fastest_time else f"{t/fastest_time:.2f}x повільніше"
        print(f"{method:<25} {t:<15.2f} {speedup:<15}")
    
    print(f"\n📝 ПОЯСНЕННЯ РІЗНИЦІ:")
    print(f"\n1️⃣  АСИНХРОННИЙ (asyncio) - найшвидший для I/O операцій:")
    print(f"   • Використовує один потік та event loop")
    print(f"   • Переключається між задачами під час очікування I/O")
    print(f"   • Мінімальні накладні витрати на переключення контексту")
    print(f"   • Ідеально для HTTP запитів та інших I/O операцій")
    
    print(f"\n2️⃣  MULTIPROCESSING - паралелізм через окремі процеси:")
    print(f"   • Створює {num_requests} окремих Python процесів")
    print(f"   • Кожен процес має власний GIL та пам'ять")
    print(f"   • Великі накладні витрати на створення процесів (~0.1-0.5сек)")
    print(f"   • Добре для CPU-bound задач, але надмірно для HTTP запитів")
    print(f"   • Час ≈ час створення процесів + час запиту")
    
    print(f"\n3️⃣  СИНХРОННИЙ - найповільніший:")
    print(f"   • Виконує запити один за одним")
    print(f"   • Блокує виконання на кожному запиті")
    print(f"   • Час ≈ {num_requests} × 2 секунди = {num_requests * 2} секунд")
    
    print(f"\n💡 ВИСНОВОК:")
    print(f"   Для I/O-bound задач (HTTP, файли, БД):")
    print(f"   ✅ Використовуйте asyncio (найкраща продуктивність)")
    print(f"   ⚠️  Multiprocessing - надмірно (великі накладні витрати)")
    print(f"   ❌ Синхронний код - найгірший варіант")
    print(f"\n   Для CPU-bound задач (обчислення, обробка даних):")
    print(f"   ✅ Використовуйте multiprocessing")
    print(f"   ❌ Asyncio не допоможе (обмеження GIL)")


def main():
    """Головна функція"""
    url = "https://httpbin.org/delay/2"
    num_requests = 5
    
    print("\n" + "="*60)
    print("🚀 ТЕСТУВАННЯ MULTIPROCESSING")
    print("="*60)
    
    # Виконуємо запити через multiprocessing
    mp_time = multiprocessing_http_requests(url, num_requests)
    
    # Для порівняння можна запустити і інші методи
    # Але вони вже є в async_vs_sync_requests.py
    
    print(f"\n{'='*60}")
    print("ℹ️  Для повного порівняння запустіть async_vs_sync_requests.py")
    print("   та порівняйте час з цим результатом")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Необхідно для Windows
    mp.freeze_support()
    
    # Встановлення необхідних бібліотек:
    # pip install requests
    main()
