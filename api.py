from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from cyber import explain
from engine import analyze, get_model

get_model()
app = FastAPI(title="ScamShield API")
WEB_PAGE = Path(__file__).parent / "web" / "index.html"

class CheckRequest(BaseModel):
    text: str = Field(max_length=5000)
    look_deeper: bool = False
    lang: Literal["en", "bn", "bnl"] = "en"

@app.get("/")
def home():
    return FileResponse(WEB_PAGE)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/check")
def check(request: CheckRequest):
    try:
        result = analyze(request.text, request.look_deeper)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    result["cyber"] = explain(result, request.lang)
    return result