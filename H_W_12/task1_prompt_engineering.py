"""
=============================================================
ЗАВДАННЯ 1: Prompt Engineering (Groq версія)
Задача: Класифікація тональності тексту (Sentiment Analysis)
3 підходи: Role Prompting, Few-Shot, Chain-of-Thought
=============================================================
pip install groq python-dotenv
=============================================================
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ─── Тексти для аналізу ────────────────────────────────────
TEXTS = [
    "Це найкращий продукт, який я коли-небудь купував! Абсолютно задоволений.",
    "Доставка затрималась на тиждень, підтримка не відповідає. Жахливо.",
    "Товар прийшов вчасно. Якість відповідає опису.",
]


# ══════════════════════════════════════════════════════════
# ПІДХІД 1: Role Prompting
# ══════════════════════════════════════════════════════════
def role_prompting(text: str) -> str:
    """
    Даємо моделі чітку роль — вона «входить» у неї
    і відповідає відповідно до рольових очікувань.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ти — провідний аналітик із NLP та sentiment analysis "
                    "з 10-річним досвідом роботи в індустрії e-commerce. "
                    "Твоя задача — точно визначати тональність відгуків клієнтів. "
                    "Відповідай лише одним словом: POSITIVE, NEGATIVE або NEUTRAL."
                ),
            },
            {"role": "user", "content": f"Визнач тональність: '{text}'"},
        ],
        max_tokens=10,
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()


# ══════════════════════════════════════════════════════════
# ПІДХІД 2: Few-Shot Prompting
# ══════════════════════════════════════════════════════════
def few_shot_prompting(text: str) -> str:
    """
    Надаємо приклади «вхід → вихід», щоб модель зрозуміла
    формат і навчилась на прикладах без explicit правил.
    """
    examples = """
Приклади:
Текст: "Чудовий сервіс, все сподобалось!"
Тональність: POSITIVE

Текст: "Не рекомендую, якість жахлива."
Тональність: NEGATIVE

Текст: "Замовлення виконано. Питань немає."
Тональність: NEUTRAL

Текст: "Швидка доставка, але упаковка пошкоджена."
Тональність: NEGATIVE

Текст: "Відмінна ціна за таку якість, дуже задоволений!"
Тональність: POSITIVE
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{examples}\n"
                    f"Текст: \"{text}\"\n"
                    "Тональність:"
                ),
            }
        ],
        max_tokens=10,
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()


# ══════════════════════════════════════════════════════════
# ПІДХІД 3: Chain-of-Thought (CoT) Prompting
# ══════════════════════════════════════════════════════════
def chain_of_thought_prompting(text: str) -> str:
    """
    Просимо модель міркувати крок за кроком перед відповіддю.
    Це підвищує точність на складних/неоднозначних прикладах.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Ти аналітик тональності тексту.",
            },
            {
                "role": "user",
                "content": (
                    f"Проаналізуй тональність наступного тексту покроково:\n\n"
                    f"Текст: \"{text}\"\n\n"
                    "Крок 1: Визнач ключові слова та фрази.\n"
                    "Крок 2: Оціни їх емоційне забарвлення.\n"
                    "Крок 3: Зваж позитивні та негативні сигнали.\n"
                    "Крок 4: Зроби фінальний висновок.\n"
                    "Відповідь на останньому рядку: SENTIMENT: [POSITIVE/NEGATIVE/NEUTRAL]"
                ),
            },
        ],
        max_tokens=300,
        temperature=0,
    )
    full = (response.choices[0].message.content or "").strip()
    for line in reversed(full.split("\n")):
        if "SENTIMENT:" in line:
            return line.split("SENTIMENT:")[-1].strip()
    return full


# ══════════════════════════════════════════════════════════
# ЗАПУСК ТА ПОРІВНЯННЯ
# ══════════════════════════════════════════════════════════
def run_comparison():
    print("=" * 65)
    print("ПОРІВНЯННЯ ПІДХОДІВ PROMPT ENGINEERING")
    print(f"Модель: {MODEL}")
    print("Задача: Sentiment Analysis")
    print("=" * 65)

    for i, text in enumerate(TEXTS, 1):
        print(f"\n📝 Текст #{i}: {text}\n")

        print(f"  [Role Prompting]    → ", end="", flush=True)
        print(role_prompting(text))

        print(f"  [Few-Shot]          → ", end="", flush=True)
        print(few_shot_prompting(text))

        print(f"  [Chain-of-Thought]  → ", end="", flush=True)
        print(chain_of_thought_prompting(text))

    print("\n" + "=" * 65)
    print("ВИСНОВКИ")
    print("=" * 65)
    print("""
┌─────────────────┬──────────────┬───────────────────────────────────┐
│ Підхід          │ Токени       │ Переваги / Недоліки               │
├─────────────────┼──────────────┼───────────────────────────────────┤
│ Role Prompting  │ Мало (~10)   │ + Швидко, дешево                  │
│                 │              │ - Менш точний на граничних кейсах  │
├─────────────────┼──────────────┼───────────────────────────────────┤
│ Few-Shot        │ Середньо     │ + Навчає на прикладах, стабільний │
│                 │ (~150 вхід)  │ - Потребує якісних прикладів       │
├─────────────────┼──────────────┼───────────────────────────────────┤
│ Chain-of-Thought│ Багато       │ + Найточніший на складних кейсах  │
│                 │ (~300 вихід) │ - Трохи повільніший                │
└─────────────────┴──────────────┴───────────────────────────────────┘

Висновок:
• Role Prompting — ідеальний для простих однозначних завдань
• Few-Shot — найкращий баланс точності та вартості в production
• Chain-of-Thought — для складних кейсів де важливе пояснення рішення
""")


if __name__ == "__main__":
    run_comparison()
