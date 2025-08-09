"""
json_formatter.py

Simple formatter that wraps answers into the API response shape expected for HackRx:
{
  "answers": [ ... ]
}
"""

from typing import List, Dict


def format_answers(answers: List[str]) -> Dict:
    """
    Wrap a list of textual answers into the final response dict.
    """
    return {"answers": answers}