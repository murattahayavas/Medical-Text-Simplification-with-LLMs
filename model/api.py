import sys
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from main import klinik_metin_isleme_sistemi


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

app = FastAPI(title="Klinik Metin Basitlestirme API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SimplifyResponse(BaseModel):
    simplified: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/simplify", response_model=SimplifyResponse)
def simplify(payload: SimplifyRequest):
    try:
        simplified = klinik_metin_isleme_sistemi(payload.text.strip())
        return {"simplified": simplified}
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc!r}",
        ) from exc
