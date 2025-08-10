# parse_docs.py
import pdfplumber
from docx import Document

def parse_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            text.append(p.extract_text() or "")
    return "\n".join(text)

def parse_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def parse_file(path):
    p = path.lower()
    if p.endswith(".pdf"):
        return parse_pdf(path)
    elif p.endswith(".docx"):
        return parse_docx(path)
    else:
        # simplest fallback: try to read as text
        try:
            with open(path, "r", encoding="utf8") as f:
                return f.read()
        except Exception:
            return ""
