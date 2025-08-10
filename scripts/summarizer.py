# summarizer.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import math

MODEL = "google/flan-t5-small"

# Load once
_tok = AutoTokenizer.from_pretrained(MODEL)
_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)

def _chunk_for_summary(text, max_chars=800):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    cur = ""
    for p in paragraphs:
        if len(cur) + len(p) + 1 > max_chars:
            if cur.strip():
                chunks.append(cur.strip())
            cur = p
        else:
            cur += "\n" + p
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def summarize_text(text, per_chunk_tokens=120):
    """
    Summarize long text by chunking and summarizing each chunk, then joining.
    Returns short combined summary (2-6 lines).
    """
    if not text or not text.strip():
        return "No text provided."

    chunks = _chunk_for_summary(text, max_chars=1000)
    summaries = []
    for ch in chunks:
        prompt = "Summarize the following contract clause in 1-2 sentences:\n\n" + ch
        inputs = _tok(prompt, return_tensors="pt", truncation=True, max_length=512)
        out = _model.generate(**inputs, max_new_tokens=per_chunk_tokens)
        s = _tok.decode(out[0], skip_special_tokens=True)
        summaries.append(s.strip())

    # Reduce combine: take first 3 non-empty summaries
    combined = " ".join([s for s in summaries if s])[:1200]
    # Make it readable with bullets
    bullets = combined.split(". ")
    bullets = [b.strip() for b in bullets if b.strip()]
    bullets = bullets[:6]
    result = "\n".join(f"- {b.strip().rstrip('.')}" for b in bullets)
    return result
