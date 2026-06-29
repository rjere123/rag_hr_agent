"""
Ingestion pipeline for the Atlas Copco Airpower HR policy chatbot.

Reads hr_policy.pdf, splits it into chunks, embeds each chunk, and stores
everything in a persistent ChromaDB collection.
"""

# 1. Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# 2. Import configuration values
from config import (
    DATA_DIR,
    VECTORSTORE_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    CLAUDE_MODEL,
)

import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

PDF_PATH = DATA_DIR / "hr_policy.pdf"


def extract_text(pdf_path):
    """3. Extract and concatenate text from every page of the PDF."""
    full_text = ""
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text


def split_text(text):
    """4. Split text into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_text(text)


def build_collection():
    """5 & 6. Create a persistent Chroma client and a fresh collection."""
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))

    # Drop any existing collection so we always start fresh.
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    # ChromaDB's default embedding function — this is the all-MiniLM-L6-v2
    # model named in config.EMBEDDING_MODEL, served as an ONNX build.
    embed_fn = embedding_functions.DefaultEmbeddingFunction()

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )
    return collection


def main():
    # 3. Extract
    text = extract_text(PDF_PATH)

    # 4. Split
    chunks = split_text(text)

    # 5 & 6. Collection + embedding function
    collection = build_collection()

    # 7. Add all chunks with ids chunk_0, chunk_1, ...
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)

    stored_count = collection.count()

    # 8. Print summary
    print("=" * 55)
    print("INGESTION COMPLETE")
    print("=" * 55)
    print(f"Total characters extracted from PDF : {len(text):,}")
    print(f"Total chunks created                : {len(chunks)}")
    print(f"Chunks stored in ChromaDB           : {stored_count}")
    if stored_count == len(chunks):
        print(f"\nAll {stored_count} chunks were successfully stored in "
              f"ChromaDB collection '{COLLECTION_NAME}'.")
    else:
        print(f"\nWARNING: mismatch — created {len(chunks)} chunks but "
              f"stored {stored_count}.")
    print("=" * 55)


if __name__ == "__main__":
    main()
