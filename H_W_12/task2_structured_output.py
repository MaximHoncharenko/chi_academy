"""
=============================================================
ЗАВДАННЯ 2: Structured Output з Pydantic (Groq версія)
Задача: Витяг структурованих даних з відгуку клієнта
=============================================================
pip install groq pydantic python-dotenv
=============================================================
"""

import os
import json
from typing import Optional
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

from groq import Groq
from pydantic import BaseModel, Field, field_validator, ValidationError

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


# ══════════════════════════════════════════════════════════
# PYDANTIC МОДЕЛІ
# ══════════════════════════════════════════════════════════

class Sentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"


class ReviewAnalysis(BaseModel):
    """Структурований аналіз відгуку клієнта."""

    sentiment: Sentiment = Field(description="Загальна тональність відгуку")
    sentiment_score: float = Field(
        description="Оцінка від -1.0 (дуже негативна) до 1.0 (дуже позитивна)",
        ge=-1.0,
        le=1.0,
    )
    key_topics: list[str] = Field(
        description="Список ключових тем у відгуку",
        min_length=1,
        max_length=10,
    )
    product_rating: Optional[int] = Field(
        default=None,
        description="Передбачувана оцінка від 1 до 5 зірок",
        ge=1,
        le=5,
    )
    issues: list[str] = Field(default=[], description="Список виявлених проблем")
    positives: list[str] = Field(default=[], description="Список позитивних моментів")
    action_required: bool = Field(description="Чи потрібна реакція служби підтримки")
    summary: str = Field(description="Короткий підсумок у 1-2 реченнях", max_length=300)
    language: str = Field(description="Мова відгуку (ISO 639-1: 'uk', 'en' тощо)")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        valid = {"uk", "en", "de", "fr", "es", "pl", "ru", "it", "pt"}
        if v.lower() not in valid:
            raise ValueError(f"Мова '{v}' не підтримується. Допустимі: {valid}")
        return v.lower()

    @field_validator("key_topics")
    @classmethod
    def deduplicate_topics(cls, v: list[str]) -> list[str]:
        seen: list[str] = []
        for item in v:
            if item.lower() not in [s.lower() for s in seen]:
                seen.append(item)
        return seen


# ══════════════════════════════════════════════════════════
# ФУНКЦІЯ АНАЛІЗУ
# ══════════════════════════════════════════════════════════

def analyze_review(review_text: str) -> ReviewAnalysis:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ти — аналітик відгуків клієнтів. "
                    "Аналізуй текст і повертай детальний структурований аналіз. "
                    "Відповідай ТІЛЬКИ валідним JSON без додаткового тексту, "
                    "без markdown, без ```json."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Проаналізуй відгук:\n\n{review_text}\n\n"
                    "Поверни JSON з полями:\n"
                    "- sentiment: POSITIVE/NEGATIVE/NEUTRAL/MIXED\n"
                    "- sentiment_score: від -1.0 до 1.0\n"
                    "- key_topics: список тем (масив рядків)\n"
                    "- product_rating: оцінка 1-5 або null\n"
                    "- issues: список проблем (масив рядків)\n"
                    "- positives: список позитивів (масив рядків)\n"
                    "- action_required: true/false\n"
                    "- summary: підсумок у 1-2 реченнях\n"
                    "- language: ISO 639-1 код мови"
                ),
            },
        ],
        temperature=0,
    )

    raw = (response.choices[0].message.content or "{}").strip()

    # Прибираємо ```json якщо модель все ж додала
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)

    try:
        return ReviewAnalysis(**data)
    except ValidationError as e:
        print(f"Помилка валідації Pydantic:\n{e}")
        raise


def print_analysis(review: str, analysis: ReviewAnalysis):
    print("\n" + "─" * 60)
    print(f"ВІДГУК:\n{review}")
    print("─" * 60)
    print(f"Тональність:    {analysis.sentiment.value}")
    print(f"Оцінка (-1→1): {analysis.sentiment_score:+.2f}")
    print(f"Рейтинг (1-5): {analysis.product_rating or 'не визначено'}")
    print(f"Мова:           {analysis.language}")
    print(f"Потрібна дія:   {'ТАК' if analysis.action_required else 'НІ'}")
    print(f"Теми:           {', '.join(analysis.key_topics)}")
    if analysis.positives:
        print("Позитиви:")
        for p in analysis.positives:
            print(f"  + {p}")
    if analysis.issues:
        print("Проблеми:")
        for i in analysis.issues:
            print(f"  - {i}")
    print(f"Підсумок:\n  {analysis.summary}")
    print(f"\nJSON для БД:")
    print(analysis.model_dump_json(indent=2))


REVIEWS = [
    "Замовив ноутбук тиждень тому. Доставили вчасно, упаковка ціла. "
    "Продуктивність відмінна, батарея тримає 8 годин. "
    "Єдиний мінус — клавіатура трохи гучна. В цілому дуже задоволений!",

    "Жахливий досвід! Чекав замовлення 3 тижні замість 5 днів. "
    "Коли нарешті отримав — товар виявився бракованим. "
    "Служба підтримки ігнорує мої повідомлення вже 4 дні. Повна катастрофа.",

    "Продукт виглядає як на фото. Доставка — 3 дні. "
    "Ціна середня по ринку. Поки що все працює нормально.",
]


def run_structured_output():
    print("=" * 60)
    print("ЗАВДАННЯ 2: STRUCTURED OUTPUT З PYDANTIC")
    print(f"Модель: {MODEL}")
    print("=" * 60)

    for i, review in enumerate(REVIEWS, 1):
        print(f"\n{'=' * 60}\nВІДГУК #{i}")
        try:
            analysis = analyze_review(review.strip())
            print_analysis(review.strip(), analysis)
        except Exception as e:
            print(f"Помилка: {e}")

    print(f"\n{'=' * 60}")
    print("Pydantic переваги:")
    print("  • Автоматична валідація типів")
    print("  • Кастомні валідатори (@field_validator)")
    print("  • Серіалізація в JSON/dict")
    print("  • IDE autocomplete та type hints")
    print("  • Чіткий контракт між LLM та додатком")


if __name__ == "__main__":
    run_structured_output()
