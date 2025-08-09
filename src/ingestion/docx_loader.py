import os
import pdfplumber
import requests
from src.config import DOCUMENTS_DIR, TEMP_DOWNLOAD_PATH

def load_pdf(file_name_or_url: str):
    """
    Loads and extracts text from a PDF file.
    Supports both local file paths and URLs.

    Args:
        file_name_or_url (str): Local filename or full URL.

    Returns:
        list of dict: Each dict contains page_num and page_text.
    """
    # If it's a URL, download temporarily
    if file_name_or_url.lower().startswith("http"):
        local_path = os.path.join(TEMP_DOWNLOAD_PATH, "temp_policy.pdf")
        os.makedirs(TEMP_DOWNLOAD_PATH, exist_ok=True)
        response = requests.get(file_name_or_url)
        with open(local_path, "wb") as f:
            f.write(response.content)
        file_path = local_path
    else:
        file_path = os.path.join(DOCUMENTS_DIR, file_name_or_url)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    pages_data = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                pages_data.append({
                    "page_num": i,
                    "page_text": text.strip()
                })
    return pages_data