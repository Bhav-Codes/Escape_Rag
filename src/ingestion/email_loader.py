"""
email_loader.py
---------------
Extracts text content from email files (.eml) or raw email strings
using the 'mail-parser' library.
"""

import os
import mailparser
from src.config import DOCUMENTS_DIR

def load_email(file_name: str):
    """
    Loads and extracts text content from an email file.

    Args:
        file_name (str): The name of the email file inside DOCUMENTS_DIR.

    Returns:
        dict: Contains subject, from, to, and body text.
    """
    file_path = os.path.join(DOCUMENTS_DIR, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Email file not found: {file_path}")

    # Parse the email using mailparser
    mail = mailparser.parse_from_file(file_path)

    # Extract fields
    email_data = {
        "subject": mail.subject,
        "from": mail.from_[0][1] if mail.from_ else None,
        "to": [addr[1] for addr in mail.to] if mail.to else [],
        "body_text": mail.body.strip() if mail.body else ""
    }

    return email_data