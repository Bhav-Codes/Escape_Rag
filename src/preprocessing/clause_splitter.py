"""
clause_splitter.py
------------------
Splits cleaned text into chunks/clauses for semantic search.
Uses configurable chunk size and overlap from config.py.
"""

from typing import List, Dict
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

def split_into_clauses(text: str, source_name: str, page_or_para: int) -> List[Dict]:
    """
    Splits text into overlapping chunks for better semantic retrieval.

    Args:
        text (str): Cleaned text to split.
        source_name (str): Name of the source document (for references).
        page_or_para (int): Page number (for PDFs) or paragraph number (for DOCX).

    Returns:
        List[Dict]: List of clauses with metadata.
    """
    clauses = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + CHUNK_SIZE, text_length)
        chunk = text[start:end].strip()

        if chunk:
            clauses.append({
                "content": chunk,
                "source": source_name,
                "location": page_or_para
            })

        start += CHUNK_SIZE - CHUNK_OVERLAP  # Move forward with overlap

    return clauses