"""
Простий скрипт для тестування API
Запустіть його після запуску сервера: python test_api.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def print_response(response, operation):
    print(f"\n{'='*60}")
    print(f"Операція: {operation}")
    print(f"Status Code: {response.status_code}")
    if response.status_code != 204:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print('='*60)


def main():
    print("🚀 Початок тестування API...")
    
    # 1. Створення користувачів
    print("\n1️⃣ Створення користувачів...")
    
    user1 = {
        "name": "Іван Петренко",
        "email": "ivan@example.com",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/users", json=user1)
    print_response(response, "CREATE user 1")
    
    user2 = {
        "name": "Марія Коваленко",
        "email": "maria@example.com",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/users", json=user2)
    print_response(response, "CREATE user 2")
    
    user3 = {
        "name": "Олександр Шевченко",
        "email": "alex@example.com",
        "is_active": False
    }
    response = requests.post(f"{BASE_URL}/users", json=user3)
    print_response(response, "CREATE user 3")
    
    # 2. Отримання всіх користувачів
    print("\n2️⃣ Отримання всіх користувачів...")
    response = requests.get(f"{BASE_URL}/users")
    print_response(response, "GET all users")
    
    # 3. Отримання одного користувача
    print("\n3️⃣ Отримання користувача з ID=1...")
    response = requests.get(f"{BASE_URL}/users/1")
    print_response(response, "GET user by ID")
    
    # 4. Оновлення користувача
    print("\n4️⃣ Оновлення користувача з ID=1...")
    update_data = {
        "name": "Іван Петренко (оновлено)",
        "is_active": False
    }
    response = requests.put(f"{BASE_URL}/users/1", json=update_data)
    print_response(response, "UPDATE user")
    
    # 5. Перевірка оновлення
    print("\n5️⃣ Перевірка оновлення...")
    response = requests.get(f"{BASE_URL}/users/1")
    print_response(response, "GET updated user")
    
    # 6. Спроба створити користувача з дублікатним email
    print("\n6️⃣ Спроба створити користувача з існуючим email...")
    duplicate_user = {
        "name": "Тест",
        "email": "maria@example.com"
    }
    response = requests.post(f"{BASE_URL}/users", json=duplicate_user)
    print_response(response, "CREATE user with duplicate email (should fail)")
    
    # 7. Видалення користувача
    print("\n7️⃣ Видалення користувача з ID=3...")
    response = requests.delete(f"{BASE_URL}/users/3")
    print_response(response, "DELETE user")
    
    # 8. Перевірка видалення
    print("\n8️⃣ Спроба отримати видаленого користувача...")
    response = requests.get(f"{BASE_URL}/users/3")
    print_response(response, "GET deleted user (should fail)")
    
    # 9. Фінальний список користувачів
    print("\n9️⃣ Фінальний список користувачів...")
    response = requests.get(f"{BASE_URL}/users")
    print_response(response, "GET all users (final)")
    
    print("\n✅ Тестування завершено!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Помилка: Не вдалося підключитися до сервера.")
        print("Переконайтеся, що сервер запущено: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
