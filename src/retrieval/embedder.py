"""
embedder.py

Create embeddings for text chunks using sentence-transformers.
This provides a simple function to convert a list of texts -> numpy vectors.
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL_NAME

# create a single global model instance for reuse
MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Convert a list of strings into embedding vectors.

    Args:
        texts: List[str] - list of textual chunks

    Returns:
        np.ndarray of shape (len(texts), embedding_dim)
    """
    if not texts:
        return np.zeros((0, MODEL.get_sentence_embedding_dimension()))

    # SentenceTransformer returns a numpy array directly
    embeddings = MODEL.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings