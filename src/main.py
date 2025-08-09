"""
main.py

Reads input from 'input.json' in the project root.

Expected format:
{
    "documents": "<URL or local filename>",
    "questions": ["Q1", "Q2", ...]
}

Runs the document QA pipeline and prints the answers JSON.
"""

import json
import os
import uuid
from typing import List, Dict

from src.ingestion.pdf_loader import load_pdf
from src.preprocessing.text_cleaner import clean_text
from src.preprocessing.clause_splitter import split_into_clauses
from src.retrieval.vector_store import build_faiss_index, search
from src.reasoning.decision_engine import answer_question
from src.output.json_formatter import format_answers


def document_to_chunks(doc_pages: List[Dict], doc_name: str) -> List[Dict]:
    """
    Convert page-level dicts into chunk dicts suitable for FAISS.
    Each chunk will have 'content', 'source', and 'location' fields.
    """
    chunks = []
    for page in doc_pages:
        page_num = page.get("page_num")
        raw = page.get("page_text", "")
        cleaned = clean_text(raw)
        page_chunks = split_into_clauses(cleaned, doc_name, page_num)
        for c in page_chunks:
            c["id"] = str(uuid.uuid4())
        chunks.extend(page_chunks)
    return chunks


def run_pipeline(document_url_or_path: str, questions: List[str]) -> Dict:
    """
    Full pipeline:
      1) load PDF (URL or local)
      2) convert to chunks and build FAISS index
      3) for each question: search, call Gemini, collect answers
    """
    # Ingest
    pages = load_pdf(document_url_or_path)

    # Chunking
    chunks = document_to_chunks(pages, document_url_or_path)

    # Build vector store
    build_faiss_index(chunks)

    # QA loop
    answers = []
    for q in questions:
        retrieved = search(q, k=6)
        answer = answer_question(q, retrieved)
        answers.append(answer)

    return format_answers(answers)


if __name__ == "__main__":
    # Path to input.json (always in project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(project_root, "input.json")

    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found in project root.")
        exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    document_url_or_path = data.get("documents")
    questions = data.get("questions", [])

    if not document_url_or_path or not questions:
        print("Error: 'input.json' must contain 'documents' and 'questions'.")
        exit(1)

    result = run_pipeline(document_url_or_path, questions)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # output_file = os.path.join(project_root, "output.json")
    # with open(output_file, "w", encoding="utf-8") as out_f:
    #     json.dump(result, out_f, ensure_ascii=False, indent=2)

    # print(f"Output saved to {output_file}")
    # print(json.dumps(result, ensure_ascii=False, indent=2))