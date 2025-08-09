"""
config.py

Central configuration for the project. All path / model constants live here.
"""

import os

# === Project paths ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "data", "documents")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
TEMP_DOWNLOAD_PATH = os.path.join(PROJECT_ROOT, "data", "temp")

# ensure processed/temp directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)

# === Embedding model (sentence-transformers) ===
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# === Vector store path ===
VECTOR_STORE_PATH = os.path.join(PROCESSED_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(PROCESSED_DIR, "chunks_metadata.json")

# === Chunking config ===
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))       # increase for legal text; chars
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))  # overlap chars

# === Gemini / Google Generative AI ===
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # must be present in your .env / env