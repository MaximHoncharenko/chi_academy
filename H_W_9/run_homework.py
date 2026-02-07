#!/usr/bin/env python3
"""
Головний скрипт для запуску всього домашнього завдання
Дозволяє вибрати, які тести запустити
"""

import sys
import subprocess
import time


def print_header(text):
    """Виводить красивий заголовок"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_menu():
    """Виводить меню вибору"""
    print_header("🎯 ДОМАШНЄ ЗАВДАННЯ: АСИНХРОННЕ ПРОГРАМУВАННЯ")
    
    print("Оберіть, що запустити:\n")
    print("  1️⃣  Завдання 1: Async vs Sync HTTP запити")
    print("  2️⃣  Завдання 1*: Multiprocessing HTTP запити")
    print("  3️⃣  Завдання 1 (всі методи): Комплексне тестування")
    print("  4️⃣  Завдання 2: FastAPI Server (потрібно 2 термінали)")
    print("  5️⃣  Завдання 2: FastAPI Client (запустити після серверу)")
    print("  6️⃣  Запустити ВСЕ (крім FastAPI)")
    print("  7️⃣  Показати діаграми та пояснення")
    print("  8️⃣  Перевірити залежності")
    print("  0️⃣  Вихід")
    print("\n" + "="*70)


def check_dependencies():
    """Перевіряє наявність необхідних бібліотек"""
    print_header("🔍 ПЕРЕВІРКА ЗАЛЕЖНОСТЕЙ")
    
    required = {
        'aiohttp': 'aiohttp',
        'requests': 'requests',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn'
    }
    
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - НЕ ВСТАНОВЛЕНО")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Відсутні залежності: {', '.join(missing)}")
        print(f"\nВстановіть їх командою:")
        print(f"  pip install {' '.join(missing)}")
        return False
    else:
        print(f"\n✅ Всі залежності встановлено!")
        return True


def run_script(script_name, description):
    """Запускає Python скрипт"""
    print_header(f"🚀 ЗАПУСК: {description}")
    
    try:
        print(f"Виконується: python {script_name}\n")
        result = subprocess.run(
            [sys.executable, script_name],
            cwd='.',
            check=False
        )
        
        if result.returncode == 0:
            print(f"\n✅ {description} - УСПІШНО ЗАВЕРШЕНО")
        else:
            print(f"\n⚠️ {description} - завершено з кодом {result.returncode}")
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print(f"\n❌ Помилка: файл {script_name} не знайдено!")
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Виконання перервано користувачем")
        return False
    except Exception as e:
        print(f"\n❌ Помилка при запуску: {e}")
        return False


def show_diagrams():
    """Показує вміст файлу з діаграмами"""
    print_header("📊 ДІАГРАМИ ТА ПОЯСНЕННЯ")
    
    try:
        with open('DIAGRAMS.md', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except FileNotFoundError:
        print("❌ Файл DIAGRAMS.md не знайдено")


def show_server_instructions():
    """Показує інструкції для запуску сервера"""
    print_header("📝 ІНСТРУКЦІЇ ДЛЯ FASTAPI")
    
    print("Для тестування FastAPI потрібно 2 термінали:\n")
    print("ТЕРМІНАЛ 1 (Сервер):")
    print("  python server.py")
    print("\nТЕРМІНАЛ 2 (Клієнт):")
    print("  python client.py")
    print("\nАбо скористайтеся опцією 4 в цьому меню для запуску сервера,")
    print("а потім опцією 5 в ІНШОМУ терміналі для запуску клієнта.")
    print("\n" + "="*70)


def run_all_tests():
    """Запускає всі тести окрім FastAPI"""
    print_header("🚀 ЗАПУСК ВСІХ ТЕСТІВ")
    
    tests = [
        ('async_vs_sync_requests.py', 'Async vs Sync'),
        ('multiprocessing_requests.py', 'Multiprocessing'),
        ('comprehensive_test.py', 'Комплексне тестування')
    ]
    
    results = []
    
    for script, description in tests:
        success = run_script(script, description)
        results.append((description, success))
        
        # Пауза між тестами
        if script != tests[-1][0]:  # Не після останнього
            print("\n⏸️  Пауза 3 секунди перед наступним тестом...")
            time.sleep(3)
    
    # Підсумок
    print_header("📊 ПІДСУМОК ТЕСТУВАННЯ")
    
    for description, success in results:
        status = "✅ УСПІХ" if success else "❌ ПОМИЛКА"
        print(f"  {description:<40} {status}")
    
    print("\n" + "="*70)


def main():
    """Головна функція"""
    
    while True:
        print_menu()
        
        try:
            choice = input("\nВаш вибір (0-8): ").strip()
            
            if choice == '0':
                print("\n👋 До побачення!")
                break
                
            elif choice == '1':
                run_script('async_vs_sync_requests.py', 'Async vs Sync HTTP')
                
            elif choice == '2':
                run_script('multiprocessing_requests.py', 'Multiprocessing HTTP')
                
            elif choice == '3':
                run_script('comprehensive_test.py', 'Комплексне тестування')
                
            elif choice == '4':
                show_server_instructions()
                if input("\nЗапустити сервер? (y/n): ").lower() == 'y':
                    run_script('server.py', 'FastAPI Server')
                
            elif choice == '5':
                print("\n⚠️  Переконайтесь, що сервер запущений в іншому терміналі!")
                if input("Продовжити? (y/n): ").lower() == 'y':
                    run_script('client.py', 'FastAPI Client')
                
            elif choice == '6':
                run_all_tests()
                
            elif choice == '7':
                show_diagrams()
                
            elif choice == '8':
                check_dependencies()
                
            else:
                print("\n❌ Невірний вибір! Оберіть число від 0 до 8")
            
            # Пауза перед поверненням до меню
            if choice != '0':
                input("\n📌 Натисніть Enter для повернення до меню...")
                
        except KeyboardInterrupt:
            print("\n\n👋 До побачення!")
            break
        except Exception as e:
            print(f"\n❌ Помилка: {e}")
            input("\n📌 Натисніть Enter для продовження...")


if __name__ == "__main__":
    main()
