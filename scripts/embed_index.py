# embed_index.py
import json
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
SIM_THRESHOLD = 0.45
TOP_K = 3

# Load model once at import
_model = SentenceTransformer(MODEL_NAME)

# Load clause templates
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
file_path = os.path.join(BASE_DIR, "data", "clause_examples.json")

with open(file_path, "r", encoding="utf8") as f:
    _clause_examples = json.load(f)

# Prepare clause texts & types
_clause_texts = []
_clause_types = []
for ctype, lst in _clause_examples.items():
    for ex in lst:
        _clause_texts.append(ex)
        _clause_types.append(ctype)

# Precompute clause embeddings and normalize
_clause_embs = _model.encode(_clause_texts, convert_to_numpy=True)
# faiss wants float32
_clause_embs = _clause_embs.astype("float32")
faiss.normalize_L2(_clause_embs)

# Build a small index
_dim = _clause_embs.shape[1]
_clause_index = faiss.IndexFlatIP(_dim)
_clause_index.add(_clause_embs)


def chunk_text(text, max_chars=800):
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


def find_clauses_from_text(text, sim_threshold=SIM_THRESHOLD, top_k=TOP_K):
    """
    Input: raw text (string)
    Output: list of {chunk: str, matches: [ {clause_type, clause_example, score}, ... ] }
    """
    chunks = chunk_text(text)
    if not chunks:
        return []

    chunk_embs = _model.encode(chunks, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(chunk_embs)
    D, I = _clause_index.search(chunk_embs, top_k)

    results = []
    for i_chunk, chunk in enumerate(chunks):
        hits = []
        for score, idx in zip(D[i_chunk], I[i_chunk]):
            if score < sim_threshold:
                continue
            hits.append({
                "clause_type": _clause_types[idx],
                "clause_example": _clause_texts[idx],
                "score": float(score)
            })
        if hits:
            results.append({"chunk": chunk, "matches": hits})
    return results


# optional helper
def get_clause_templates():
    return _clause_examples
