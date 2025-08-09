"""
qa_engine.py

Query-answering engine that:
 - collects retrieved chunks for a question
 - constructs a clear prompt for Gemini
 - enforces an output format (here: a single concise answer string)

Important:
 - This is where 'decision engine' or 'answer engine' logic lives.
 - If you want a different output schema (e.g., JSON with decision/amount/justification),
   modify the prompt template here to enforce that schema.
"""
from dotenv import load_dotenv
import os
from typing import List, Dict
import google.generativeai as genai
from src.config import GEMINI_MODEL, GOOGLE_API_KEY

load_dotenv()  # Load environment variables from .env file

# Configure Gemini client once at import-time
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function starting with underscore are private helpers (not part of public API)(Can only be used within this file)
def _build_prompt(question: str, retrieved_chunks: List[Dict]) -> str:
    """
    Create a controlled prompt that:
     - gives the model the retrieved context (top chunks)
     - instructs it to answer concisely and directly
     - instructs it to respond ONLY with the answer (no justification) unless asked
    """
    context_texts = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        # Include source/location so model can reference clauses if needed
        context_texts.append(f"[{i}] Source: {chunk.get('source')} - Loc: {chunk.get('location')}\n{chunk.get('text')}\n")

    context = "\n----\n".join(context_texts)

    prompt = (
        "You are an expert insurance-policy assistant. "
        "Answer the user's question using ONLY the provided context. "
        "If the context doesn't contain a clear answer, say 'Not stated in the document.'\n\n"
        f"QUESTION: {question}\n\n"
        "CONTEXT (relevant extracted clauses):\n"
        f"{context}\n\n"
        "INSTRUCTIONS:\n"
        " - Provide a concise, single-paragraph answer (1-3 sentences).\n"
        " - Do NOT invent facts beyond the context.\n"
        " - If the answer is present in the context, prefer quoting clause-level specifics (e.g., 'Clause X on Page Y').\n"
        " - Respond ONLY with the answer. Do NOT include 'Answer:' or any extra JSON wrappers.\n"
    )
    return prompt


def answer_question(question: str, retrieved: List[Dict]) -> str:
    """
    Produces a short answer string for a single question.

    Args:
      question: str - user's natural-language question
      retrieved: List[Dict] - top-k retrieved metadata dicts (with 'text' field)

    Returns:
      str - concise answer text
    """
    prompt = _build_prompt(question, retrieved)

    # Use a lightweight call to Gemini
    # Using generative API with minimal parameters to keep responses short and deterministic-ish.
    #-----------------
    # response = genai.generate(
    #     model=GEMINI_MODEL,
    #     prompt=prompt,
    #     max_output_tokens=256,
    #     temperature=0.0,  # deterministic
    #     top_p=0.95,
    # )
    # -----------------
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=256,
            temperature=0.0,
            top_p=0.95
    )
)

    # Gemini's Python SDK returns nested structure; .text is commonly the main content
    # but exact field can differ by SDK version — using response.candidates[0].output[0].content[0].text
    # We'll try safe extraction patterns:
    text = ""
    try:
        # Newer SDK often: response.candidates[0].content[0].text or response.text
        if hasattr(response, "text") and response.text:
            text = response.text
        else:
            # fall back to nested candidate structure
            cand = response.candidates[0]
            if hasattr(cand, "content"):
                # content may be list of dicts
                parts = []
                for c in cand.content:
                    if isinstance(c, dict) and "text" in c:
                        parts.append(c["text"])
                    elif isinstance(c, str):
                        parts.append(c)
                text = "".join(parts)
            elif hasattr(cand, "output") and cand.output:
                # older style
                text = cand.output[0].get("content", [{"text": ""}])[0].get("text", "")
    except Exception:
        # As fallback, convert to str
        text = str(response)

    # final cleanup: strip whitespace
    return text.strip()