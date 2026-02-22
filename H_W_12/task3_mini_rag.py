"""
=============================================================
ЗАВДАННЯ 3: Mini RAG (Groq версія)
Embeddings: sentence-transformers (безкоштовно, локально)
LLM: Groq llama-3.3-70b-versatile (безкоштовно)
=============================================================
pip install groq sentence-transformers python-dotenv
=============================================================
"""

import os
import math
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from groq import Groq
from sentence_transformers import SentenceTransformer

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"
DOC_PATH = Path(__file__).parent / "python_guide.md"

# Локальна модель для embeddings (завантажується один раз ~90MB)
print("Завантаження embedding моделі...")
EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding модель готова\n")


# ══════════════════════════════════════════════════════════
# 1. ЗАВАНТАЖЕННЯ ТА РОЗБИТТЯ ДОКУМЕНТА
# ══════════════════════════════════════════════════════════

def load_and_chunk(path: Path, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    text = path.read_text(encoding="utf-8")

    # Розбиваємо по розділах для логічного поділу
    sections = text.split("\n## ")
    chunks = []

    for section in sections:
        if not section.strip():
            continue
        if len(section) <= chunk_size:
            chunks.append({"text": section.strip(), "embedding": None})
        else:
            words = section.split()
            current: list[str] = []
            current_len = 0
            for word in words:
                current.append(word)
                current_len += len(word) + 1
                if current_len >= chunk_size:
                    chunks.append({"text": " ".join(current), "embedding": None})
                    current = current[-(overlap // 10):]
                    current_len = sum(len(w) + 1 for w in current)
            if current:
                chunks.append({"text": " ".join(current), "embedding": None})

    print(f"📄 Документ завантажено: {len(chunks)} чанків")
    return chunks


# ══════════════════════════════════════════════════════════
# 2. ІНДЕКСАЦІЯ — генерація embeddings
# ══════════════════════════════════════════════════════════

def build_index(chunks: list[dict]) -> list[dict]:
    print("🔄 Індексація (sentence-transformers, локально)...")
    texts = [c["text"] for c in chunks]
    embeddings = EMBEDDER.encode(texts, show_progress_bar=False)
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist()
    print(f"✅ Індексація завершена ({len(chunks)} векторів)\n")
    return chunks


# ══════════════════════════════════════════════════════════
# 3. ПОШУК РЕЛЕВАНТНИХ ФРАГМЕНТІВ
# ══════════════════════════════════════════════════════════

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x ** 2 for x in a))
    norm_b = math.sqrt(sum(x ** 2 for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    query_emb = EMBEDDER.encode([query])[0].tolist()
    scored = [
        {"text": c["text"], "score": cosine_similarity(query_emb, c["embedding"])}
        for c in chunks
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ══════════════════════════════════════════════════════════
# 4. ГЕНЕРАЦІЯ ВІДПОВІДЕЙ
# ══════════════════════════════════════════════════════════

def answer_without_context(query: str) -> str:
    """Відповідь БЕЗ RAG — тільки знання моделі."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Ти — помічник з Python. Відповідай стисло."},
            {"role": "user", "content": query},
        ],
        max_tokens=300,
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()


def answer_with_context(query: str, relevant_chunks: list[dict]) -> str:
    """Відповідь З RAG контекстом."""
    context = "\n\n---\n\n".join(
        f"[Score: {c['score']:.3f}]\n{c['text']}"
        for c in relevant_chunks
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ти — помічник з Python. Відповідай ТІЛЬКИ на основі наданого контексту. "
                    "Якщо відповіді немає в контексті — так і скажи."
                ),
            },
            {
                "role": "user",
                "content": f"Контекст:\n{context}\n\nЗапитання: {query}",
            },
        ],
        max_tokens=400,
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()


# ══════════════════════════════════════════════════════════
# 5. ПОРІВНЯННЯ
# ══════════════════════════════════════════════════════════

QUERIES = [
    "Що таке декоратори в Python і як їх використовувати?",
    "Чим відрізняється multiprocessing від asyncio?",
    "Як Poetry відрізняється від pip?",
]


def run_mini_rag():
    print("=" * 65)
    print("ЗАВДАННЯ 3: MINI RAG")
    print(f"LLM: {MODEL} (Groq)")
    print("Embeddings: sentence-transformers/all-MiniLM-L6-v2 (локально)")
    print("=" * 65)

    chunks = load_and_chunk(DOC_PATH)
    chunks = build_index(chunks)

    for i, query in enumerate(QUERIES, 1):
        print(f"\n{'=' * 65}")
        print(f"ЗАПИТ #{i}: {query}")
        print("=" * 65)

        relevant = retrieve(query, chunks, top_k=2)
        print(f"\nЗнайдені фрагменти:")
        for j, chunk in enumerate(relevant, 1):
            preview = chunk["text"][:100].replace("\n", " ")
            print(f"  [{j}] Score={chunk['score']:.4f} | {preview}...")

        print(f"\nБЕЗ КОНТЕКСТУ:")
        print(answer_without_context(query))

        print(f"\nЗ КОНТЕКСТОМ (RAG):")
        print(answer_with_context(query, relevant))

    print(f"\n{'=' * 65}")
    print("АНАЛІЗ РІЗНИЦІ:")
    print("=" * 65)
    print("""
БЕЗ контексту:              З контекстом (RAG):
• Загальні знання моделі    • Специфічна інформація з документа
• Може галюцинувати         • Заземлена у реальному тексті
• Не знає деталей проекту   • Точні деталі з документації
• Швидший                   • Посилається на джерело

Висновок: RAG значно покращує точність для специфічних
питань про конкретний документ/проект.
""")


if __name__ == "__main__":
    run_mini_rag()
