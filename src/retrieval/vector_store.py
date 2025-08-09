"""
vector_store.py

Simple wrapper around FAISS for indexing and searching chunk embeddings,
plus saving/loading index and metadata mapping.
"""

import json
import os
from typing import List, Dict, Tuple

import faiss
import numpy as np

from src.config import VECTOR_STORE_PATH, METADATA_PATH
from src.retrieval.embedder import embed_texts


def build_faiss_index(chunks: List[Dict]) -> None:
    """
    Build and persist a FAISS index from provided chunks.

    Args:
        chunks: list of dicts with keys: 'content', 'source', 'location', 'id'
    Side effects:
        - saves FAISS binary to VECTOR_STORE_PATH
        - saves metadata JSON to METADATA_PATH
    """
    # 1) Extract texts and metadata
    texts = [c["content"] for c in chunks]
    metadata = [{"id": i, "source": c["source"], "location": c["location"], "text": c["content"]} for i, c in enumerate(chunks)]

    # 2) Compute embeddings
    embeddings = embed_texts(texts).astype("float32")

    # 3) Create FAISS index (flat L2 index)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)  # add all vectors

    # 4) Persist index and metadata
    faiss.write_index(index, VECTOR_STORE_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def load_faiss_index() -> Tuple[faiss.IndexFlatL2, List[Dict]]:
    """
    Load persisted FAISS index and metadata.

    Returns:
        (index, metadata_list)
    """
    if not os.path.exists(VECTOR_STORE_PATH) or not os.path.exists(METADATA_PATH):
        raise FileNotFoundError("FAISS index or metadata not found. Please run build_faiss_index first.")

    index = faiss.read_index(VECTOR_STORE_PATH)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata


def search(query: str, k: int = 5) -> List[Dict]:
    """
    Semantic search pipeline:
      - embed query
      - search FAISS
      - return metadata entries for top-k results with distances

    Returns:
        List[ Dict(id, source, location, text, score) ]
    """
    # Load index and metadata
    index, metadata = load_faiss_index()

    # Embed query
    q_emb = embed_texts([query]).astype("float32")

    # Search
    distances, indexes = index.search(q_emb, k)
    indexes = indexes[0].tolist()
    distances = distances[0].tolist()

    results = []
    for idx, dist in zip(indexes, distances):
        if idx < 0 or idx >= len(metadata):
            continue
        item = metadata[idx].copy()
        item["score"] = float(dist)
        results.append(item)
    return results