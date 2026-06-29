"""
Retrieval engine for the Atlas Copco Airpower HR policy chatbot.

Takes a user question, retrieves the most relevant chunks from ChromaDB,
builds a grounded prompt, and asks Claude to answer using only that context.
"""

import sys

# Ensure UTF-8 console output (Claude responses may contain non-cp1252 chars).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 1. Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# 2. Import configuration values
from config import (
    DATA_DIR,
    VECTORSTORE_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
    CLAUDE_MODEL,
)

import chromadb
from chromadb.utils import embedding_functions
from anthropic import Anthropic


def _build_embedding_function():
    """
    Use ChromaDB's default embedding function (all-MiniLM-L6-v2, matching
    config.EMBEDDING_MODEL). If the ONNX model download is blocked by a
    network firewall, fall back to the SentenceTransformer implementation.
    """
    try:
        return embedding_functions.DefaultEmbeddingFunction()
    except Exception as exc:
        print(f"[warn] Default embedding function unavailable ({exc}); "
              f"falling back to SentenceTransformer '{EMBEDDING_MODEL}'.")
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )


# 3. Persistent client + existing collection (same embedding fn as ingestion)
_embed_fn = _build_embedding_function()
_client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
_collection = _client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=_embed_fn,
)

# Anthropic client (reads ANTHROPIC_API_KEY from the environment / .env)
_anthropic = Anthropic()


def _build_prompt(question: str, context: str) -> str:
    return (
        "You are an HR-assistant of Atlas copco Airpower and answer the employee "
        "question using only the context provided below. If the answer is not "
        "present in the context, say that I am sorry and that info is not present "
        "in the hr_policy doc.\n\n"
        f"Context : {context}\n\n"
        f"Question :{question}"
    )


def retrieve(question: str) -> dict:
    """Retrieve relevant chunks without calling the LLM. Returns sources + context."""
    results = _collection.query(query_texts=[question], n_results=TOP_K)
    documents = results["documents"][0]
    ids = results["ids"][0]
    distances = (results.get("distances") or [[None] * len(documents)])[0]
    context = "\n\n".join(documents)
    sources = [
        {
            "id": ids[i],
            "text": documents[i],
            "distance": distances[i] if i < len(distances) else None,
        }
        for i in range(len(documents))
    ]
    return {"sources": sources, "context": context}


def stream_response(question: str, context: str):
    """Return an Anthropic streaming context manager for the given question and context."""
    return _anthropic.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": _build_prompt(question, context)}],
    )


def get_answer_detailed(question: str) -> dict:
    """
    Answer an employee question and return the answer together with the
    retrieved source chunks and Claude's token usage.

    This is an ADDITIVE helper used by the Streamlit frontend so it can show
    citations and real telemetry. It does not change the model, prompt, or
    any generation parameters used by get_answer().

    Returns a dict:
        {
            "answer":  str,
            "sources": [{"id": str, "text": str, "distance": float | None}, ...],
            "usage":   {"input_tokens": int, "output_tokens": int},
            "context": str,
        }
    """

    # a) & b) Query the collection — Chroma embeds the question with the
    #          collection's embedding function and returns the top-K chunks.
    results = _collection.query(
        query_texts=[question],
        n_results=TOP_K,
    )
    documents = results["documents"][0]
    ids = results["ids"][0]
    distances = (results.get("distances") or [[None] * len(documents)])[0]

    # c) Join retrieved chunks into a single context string.
    context = "\n\n".join(documents)

    # d) Build the grounded prompt.
    prompt = (
        "You are an HR-assistant of Atlas copco Airpower and answer the employee "
        "question using only the context provided below. If the answer is not "
        "present in the context, say that I am sorry and that info is not present "
        "in the hr_policy doc.\n\n"
        f"Context : {context}\n\n"
        f"Question :{question}"
    )

    # e) Call the Anthropic API with the configured Claude model.
    response = _anthropic.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    sources = [
        {
            "id": ids[i],
            "text": documents[i],
            "distance": distances[i] if i < len(distances) else None,
        }
        for i in range(len(documents))
    ]

    return {
        "answer": response.content[0].text,
        "sources": sources,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        "context": context,
    }


def get_answer(question: str) -> str:
    """Answer an employee question using only the HR policy context."""
    # f) Return Claude's text response (delegates to the detailed helper).
    return get_answer_detailed(question)["answer"]


# Alias to match the name referenced in the test block.
answer_question = get_answer


# 4. Test the function with four sample questions.
if __name__ == "__main__":
    questions = [
        "What is the leave policy for casual leaves per year?",
        "What is the notice period for a senior employees?",
        "What is the max allowance for hotels on a domestic travel?",
        "What is the CEO personal phone number?",
    ]

    for i, q in enumerate(questions, start=1):
        print("=" * 70)
        print(f"Q{i}: {q}")
        print("-" * 70)
        print(answer_question(q))
        print()
