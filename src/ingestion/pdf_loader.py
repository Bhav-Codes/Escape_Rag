"""
pdf_loader.py

Load PDFs from local path or URL, extract page-level text with page numbers.
"""

import os
import requests
import pdfplumber
from urllib.parse import urlparse

from src.config import DOCUMENTS_DIR, TEMP_DOWNLOAD_PATH


def _download_to_temp(url: str, filename: str = "downloaded_policy.pdf") -> str:
    """
    Download a PDF from a URL into the TEMP_DOWNLOAD_PATH and return the local path.
    """
    os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)
    local_path = os.path.join(TEMP_DOWNLOAD_PATH, filename)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()  # raise if download failed
    with open(local_path, "wb") as f:
        f.write(resp.content)
    return local_path


def load_pdf(path_or_url: str):
    """
    Accept either a local filename (relative to DOCUMENTS_DIR) or a full URL.
    Returns a list of dicts: [{ 'page_num': int, 'page_text': str }, ...]
    """
    # If input looks like a URL (starts with http/https), download it first
    parsed = urlparse(path_or_url)
    if parsed.scheme in ("http", "https"):
        local_path = _download_to_temp(path_or_url)
    else:
        local_path = os.path.join(DOCUMENTS_DIR, path_or_url)

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"PDF not found at: {local_path}")

    pages = []
    with pdfplumber.open(local_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                pages.append({"page_num": i, "page_text": text.strip()})
    return pages