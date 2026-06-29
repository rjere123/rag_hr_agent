from pathlib import Path

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vector-store"
COLLECTION_NAME = "HR_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3
CLAUDE_MODEL = "claude-sonnet-4-6"

if __name__ == "__main__":
    print(f"DATA_DIR:        {DATA_DIR}")
    print(f"VECTORSTORE_DIR: {VECTORSTORE_DIR}")
    print(f"COLLECTION_NAME: {COLLECTION_NAME}")
    print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    print(f"CHUNK_SIZE:      {CHUNK_SIZE}")
    print(f"CHUNK_OVERLAP:   {CHUNK_OVERLAP}")
    print(f"TOP_K:           {TOP_K}")
    print(f"CLAUDE_MODEL:    {CLAUDE_MODEL}")
