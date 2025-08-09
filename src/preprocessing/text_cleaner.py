"""
text_cleaner.py
---------------
Cleans and normalizes raw text from PDFs, DOCX, and email bodies.
Ensures text is uniform before chunking or embedding.
"""

import re

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text by:
      - Removing excessive whitespace
      - Normalizing punctuation spacing
      - Removing non-printable characters

    Args:
        text (str): The raw input text.

    Returns:
        str: Cleaned and normalized text.
    """
    if not text:
        return ""

    # Remove non-printable characters
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", "", text)

    # Replace multiple spaces/tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove multiple newlines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Normalize spaces before punctuation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    # Trim leading/trailing whitespace
    text = text.strip()

    return text