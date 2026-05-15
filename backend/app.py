"""
AI Notes Summarizer - Backend API
==================================
FastAPI backend that receives text input, performs summarization
using HuggingFace Transformers (distilbart-cnn-12-6), and returns
structured JSON responses with summary + analytics.

NOTE: transformers v5.x removed the legacy "summarization" pipeline task.
We use AutoTokenizer + AutoModelForSeq2SeqLM directly for full control.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import time
import logging

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app initialisation
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Notes Summarizer API",
    description="Summarize long notes using HuggingFace distilbart-cnn-12-6",
    version="1.0.0",
)

# Allow requests from Streamlit frontend (typically on port 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load model & tokenizer once at startup
# ---------------------------------------------------------------------------
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

logger.info("Loading model '%s' – this may take a moment on first run …", MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model.eval()  # Set to inference mode

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
logger.info("Model loaded successfully on device: %s", device)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class SummarizeRequest(BaseModel):
    """Schema for the POST /summarize request body."""
    text: str


class SummarizeResponse(BaseModel):
    """Schema for the POST /summarize response body."""
    summary: str
    original_word_count: int
    summary_word_count: int
    compression_percentage: float
    processing_time: float  # seconds


# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def chunk_text(text: str, max_chunk_chars: int = 800) -> list[str]:
    """
    Split *text* into chunks of roughly *max_chunk_chars* characters,
    breaking at sentence boundaries when possible so that the model
    receives coherent segments.
    """
    sentences = text.replace("\n", " ").split(". ")
    chunks: list[str] = []
    current_chunk = ""

    for sentence in sentences:
        candidate = f"{current_chunk}. {sentence}" if current_chunk else sentence
        if len(candidate) > max_chunk_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = candidate

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def summarize_chunk(text: str) -> str:
    """
    Summarise a single text chunk using the loaded model and tokenizer.
    """
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,
        truncation=True,
    ).to(device)

    # Dynamically set max/min lengths relative to the input
    input_length = len(text.split())
    max_len = min(150, max(30, input_length // 2))
    min_len = min(30, max(10, input_length // 4))

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_len,
            min_length=min_len,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True,
        )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def summarize_text(text: str) -> str:
    """
    Summarise arbitrarily long *text* by:
      1. Splitting it into ≤ 800-char chunks
      2. Summarising each chunk individually
      3. Joining the per-chunk summaries into one final summary
    """
    chunks = chunk_text(text)
    summaries: list[str] = []

    for chunk in chunks:
        # The model needs at least ~30 characters to produce something useful
        if len(chunk.strip()) < 30:
            continue

        try:
            result = summarize_chunk(chunk)
            summaries.append(result)
        except Exception as exc:
            logger.warning("Chunk summarisation failed: %s", exc)
            continue

    return " ".join(summaries)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Simple health-check endpoint."""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "device": str(device),
        "message": "AI Notes Summarizer API is running.",
    }


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    """
    Accept a block of text, summarise it, and return the summary together
    with word-count analytics and compression percentage.
    """
    text = request.text.strip()

    # --- Validate input ---
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    if len(text) < 30:
        raise HTTPException(
            status_code=400,
            detail="Input text is too short to summarise. Please provide at least a few sentences.",
        )

    # --- Summarise ---
    start = time.time()
    summary = summarize_text(text)
    elapsed = round(time.time() - start, 2)

    if not summary:
        raise HTTPException(
            status_code=500,
            detail="The model was unable to generate a summary. Please try again with different text.",
        )

    # --- Analytics ---
    original_wc = len(text.split())
    summary_wc = len(summary.split())
    compression = round((1 - summary_wc / original_wc) * 100, 2) if original_wc else 0.0

    return SummarizeResponse(
        summary=summary,
        original_word_count=original_wc,
        summary_word_count=summary_wc,
        compression_percentage=compression,
        processing_time=elapsed,
    )


# ---------------------------------------------------------------------------
# Entry-point (for convenience when running directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
