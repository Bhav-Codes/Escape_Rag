from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

from src.main import run_pipeline  # we already wrote this function

app = FastAPI()

# Input schema matching your sample
class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

# Output schema
class HackRxResponse(BaseModel):
    answers: List[str]

@app.post("/hackrx/run", response_model=HackRxResponse)
def run_hackrx(req: HackRxRequest):
    result = run_pipeline(req.documents, req.questions)
    return result