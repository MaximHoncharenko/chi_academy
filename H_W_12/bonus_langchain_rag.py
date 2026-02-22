"""
=============================================================
БОНУС: LangChain RAG + Structured Output (Groq версія)
LLM: Groq llama-3.3-70b-versatile
Embeddings: HuggingFace all-MiniLM-L6-v2 (локально, безкоштовно)
=============================================================
pip install langchain langchain-groq langchain-community
pip install langchain-text-splitters langchain-huggingface
pip install faiss-cpu sentence-transformers python-dotenv
=============================================================
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel, Field, SecretStr
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser



# ══════════════════════════════════════════════════════════
# PYDANTIC СТРУКТУРА ВІДПОВІДІ
# ══════════════════════════════════════════════════════════

class RAGResponse(BaseModel):
    answer: str = Field(description="Відповідь на запитання")
    confidence: float = Field(description="Впевненість від 0.0 до 1.0", ge=0.0, le=1.0)
    sources_used: list[str] = Field(description="Ключові тези з документа")
    answer_found_in_docs: bool = Field(description="True якщо відповідь знайдена в документах")
    follow_up_questions: Optional[list[str]] = Field(
        default=None, description="3 пов'язаних запитання"
    )


# ══════════════════════════════════════════════════════════
# 1. ЗАВАНТАЖЕННЯ ТА ІНДЕКСАЦІЯ
# ══════════════════════════════════════════════════════════

def build_vectorstore(doc_path: str) -> FAISS:
    text = Path(doc_path).read_text(encoding="utf-8")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    docs = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": doc_path}]
    )
    print(f"📄 Розбито на {len(docs)} чанків")

    # Локальні embeddings — НЕ потребують API ключа
    print("🔄 Завантаження HuggingFace embeddings (перший раз ~90MB)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(docs, embeddings)
    print("✅ FAISS індекс побудовано\n")
    return vectorstore


# ══════════════════════════════════════════════════════════
# 2. RAG CHAIN
# ══════════════════════════════════════════════════════════

def build_rag_chain(vectorstore: FAISS):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=SecretStr(os.getenv("GROQ_API_KEY") or ""),
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )

    parser = JsonOutputParser(pydantic_object=RAGResponse)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Ти — Python-експерт. Відповідай ТІЛЬКИ на основі наданого контексту.\n"
            "Якщо відповіді немає — вкажи це чесно.\n"
            "Поверни ТІЛЬКИ валідний JSON без ```json та без зайвого тексту.\n\n"
            "{format_instructions}",
        ),
        (
            "human",
            "Контекст:\n{context}\n\nЗапитання: {question}",
        ),
    ])
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())

    def rag_chain(query: str) -> RAGResponse:
        relevant_docs: list[Document] = retriever.invoke(query)
        context = "\n\n---\n\n".join(d.page_content for d in relevant_docs)

        messages = prompt.format_messages(context=context, question=query)
        raw_response = llm.invoke(messages)

        content = raw_response.content
        if isinstance(content, list):
            content = " ".join(
                c["text"] if isinstance(c, dict) else str(c) for c in content
            )
        content = str(content).strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        parsed = json.loads(content)
        return RAGResponse(**parsed)

    return rag_chain


# ══════════════════════════════════════════════════════════
# 3. ДЕМОНСТРАЦІЯ
# ══════════════════════════════════════════════════════════

QUERIES = [
    "Як працює asyncio і чим відрізняється від multiprocessing?",
    "Які бібліотеки Python підходять для машинного навчання?",
    "Як використовувати pytest для тестування?",
]

DOC_PATH = str(Path(__file__).parent / "python_guide.md")


def run_langchain_rag():
    print("=" * 65)
    print("БОНУС: LangChain RAG + Structured Output")
    print("LLM: Groq llama-3.3-70b | Embeddings: HuggingFace (локально)")
    print("=" * 65)

    vectorstore = build_vectorstore(DOC_PATH)
    rag_chain = build_rag_chain(vectorstore)

    for i, query in enumerate(QUERIES, 1):
        print(f"\n{'=' * 65}")
        print(f"ЗАПИТ #{i}: {query}")
        print("=" * 65)

        response: RAGResponse = rag_chain(query)

        print(f"\nВІДПОВІДЬ:\n  {response.answer}")
        print(f"\nВпевненість:   {response.confidence:.0%}")
        print(f"З документів:  {'ТАК' if response.answer_found_in_docs else 'НІ'}")
        print(f"\nВикористані тези:")
        for src in response.sources_used:
            print(f"  • {src}")
        if response.follow_up_questions:
            print(f"\nНаступні запитання:")
            for fq in response.follow_up_questions:
                print(f"  → {fq}")

    print(f"\n{'=' * 65}")
    print("LangChain pipeline:")
    print("  Query -> HuggingFace Embeddings -> FAISS -> Top-K Docs")
    print("  -> ChatPromptTemplate -> Groq LLM -> JsonOutputParser -> RAGResponse")


if __name__ == "__main__":
    run_langchain_rag()
