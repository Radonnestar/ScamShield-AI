import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from cyber import explain
from engine import analyze, get_model
from reasons_i18n import translate_reason

get_model()
app = FastAPI(title="ScamShield API")
WEB_PAGE = Path(__file__).parent / "web" / "index.html"

# ---- Rate limiting: a simple "N requests per minute per visitor" counter ----
WINDOW_SECONDS = 60
LIMITS = {"check": 30, "deep": 6, "url": 90}   # "deep" = look_deeper, which contacts outside services
_hits = defaultdict(deque)                     # (visitor, kind) -> times of recent requests


def rate_limit(request: Request, kind: str):
    visitor = request.client.host if request.client else "unknown"
    now = time.monotonic()
    recent = _hits[(visitor, kind)]
    while recent and now - recent[0] > WINDOW_SECONDS:
        recent.popleft()                       # forget requests older than a minute
    if len(recent) >= LIMITS[kind]:
        raise HTTPException(status_code=429, detail="Too many requests. Wait a minute and try again.")
    recent.append(now)


class CheckRequest(BaseModel):
    text: str = Field(max_length=5000)
    look_deeper: bool = False
    lang: Literal["en", "bn", "bnl"] = "en"


class UrlRequest(BaseModel):
    url: str = Field(max_length=2000)
    lang: Literal["en", "bn", "bnl"] = "en"


@app.get("/")
def home():
    return FileResponse(WEB_PAGE)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check(body: CheckRequest, request: Request):
    rate_limit(request, "deep" if body.look_deeper else "check")
    try:
        result = analyze(body.text, body.look_deeper)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    for link in result.get("links", []):
        link["reasons"] = [translate_reason(r, body.lang) for r in link.get("reasons", [])]
    result["cyber"] = explain(result, body.lang)
    return result


@app.post("/check-url")
def check_url(body: UrlRequest, request: Request):
    """Used by the browser extension: judge one web address, ignoring the text model."""
    rate_limit(request, "url")
    try:
        result = analyze(body.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    links = result.get("links", [])
    flagged = bool((result.get("threat_list") or {}).get("flagged"))
    if not links:
        return {"level": "unknown", "score": 0, "reasons": [], "flagged": flagged}
    worst = max(links, key=lambda l: l["score"])
    return {
        "level": "risky" if flagged else worst["level"],
        "score": worst["score"],
        "reasons": [translate_reason(r, body.lang) for r in worst.get("reasons", [])],
        "flagged": flagged,
    }