"""
Завдання 2: FastAPI сервер з blocking та non-blocking ендпоінтами
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio
import time
from datetime import datetime

app = FastAPI(title="Blocking vs Non-Blocking Demo")


# Лічильник для відстеження запитів
request_counters = {
    "blocking": 0,
    "non_blocking": 0
}


@app.get("/")
async def root():
    """Головна сторінка з інформацією"""
    return {
        "message": "Blocking vs Non-Blocking Demo Server",
        "endpoints": {
            "/blocking": "Використовує time.sleep(2) - блокує потік",
            "/non-blocking": "Використовує await asyncio.sleep(2) - не блокує",
            "/stats": "Статистика запитів"
        },
        "info": {
            "blocking_requests": request_counters["blocking"],
            "non_blocking_requests": request_counters["non_blocking"]
        }
    }


@app.get("/blocking")
def blocking_endpoint():
    """
    ❌ БЛОКУЮЧИЙ ендпоінт
    
    Використовує time.sleep(), який БЛОКУЄ весь потік виконання.
    Під час sleep() сервер НЕ МОЖЕ обробляти інші запити в цьому worker'і.
    """
    request_counters["blocking"] += 1
    request_num = request_counters["blocking"]
    
    start_time = time.time()
    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"🔴 [{current_time}] Blocking запит #{request_num} ПОЧАТО - thread ЗАБЛОКУЄТЬСЯ на 2 сек")
    
    # ❌ БЛОКУЄ весь потік - інші запити чекають!
    time.sleep(2)
    
    end_time = time.time()
    duration = end_time - start_time
    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"🔴 [{current_time}] Blocking запит #{request_num} ЗАВЕРШЕНО за {duration:.3f}s")
    
    return JSONResponse({
        "endpoint": "blocking",
        "request_number": request_num,
        "method": "time.sleep(2)",
        "duration": round(duration, 3),
        "behavior": "БЛОКУЄ потік - інші запити чекають",
        "timestamp": current_time
    })


@app.get("/non-blocking")
async def non_blocking_endpoint():
    """
    ✅ НЕ-БЛОКУЮЧИЙ ендпоінт
    
    Використовує await asyncio.sleep(), який НЕ БЛОКУЄ event loop.
    Під час sleep() сервер МОЖЕ обробляти інші запити.
    """
    request_counters["non_blocking"] += 1
    request_num = request_counters["non_blocking"]
    
    start_time = time.time()
    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"🟢 [{current_time}] Non-blocking запит #{request_num} ПОЧАТО - event loop ВІЛЬНИЙ")
    
    # ✅ НЕ БЛОКУЄ event loop - інші запити обробляються паралельно!
    await asyncio.sleep(2)
    
    end_time = time.time()
    duration = end_time - start_time
    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"🟢 [{current_time}] Non-blocking запит #{request_num} ЗАВЕРШЕНО за {duration:.3f}s")
    
    return JSONResponse({
        "endpoint": "non-blocking",
        "request_number": request_num,
        "method": "await asyncio.sleep(2)",
        "duration": round(duration, 3),
        "behavior": "НЕ БЛОКУЄ event loop - запити обробляються паралельно",
        "timestamp": current_time
    })


@app.get("/stats")
async def stats():
    """Статистика запитів"""
    return {
        "total_blocking_requests": request_counters["blocking"],
        "total_non_blocking_requests": request_counters["non_blocking"],
        "info": {
            "blocking": "Використовує time.sleep() - блокує потік",
            "non_blocking": "Використовує await asyncio.sleep() - не блокує event loop"
        }
    }


@app.get("/reset")
async def reset_stats():
    """Скидання статистики"""
    request_counters["blocking"] = 0
    request_counters["non_blocking"] = 0
    return {"message": "Статистика скинута", "counters": request_counters}


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 ЗАПУСК FASTAPI СЕРВЕРА")
    print("="*60)
    print("\n📌 Доступні ендпоінти:")
    print("   • http://localhost:8000/blocking     - блокуючий (time.sleep)")
    print("   • http://localhost:8000/non-blocking - не-блокуючий (asyncio.sleep)")
    print("   • http://localhost:8000/stats        - статистика")
    print("   • http://localhost:8000/reset        - скинути статистику")
    print("\n💡 Запустіть client.py в іншому терміналі для тестування")
    print("="*60 + "\n")
    
    # Запускаємо сервер з одним worker'ом для наочності
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
