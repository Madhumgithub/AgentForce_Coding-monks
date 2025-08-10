# parse_docs.py

import pdfplumber
from docx import Document

def parse_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def parse_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_file(path):
    if path.lower().endswith(".pdf"):
        return parse_pdf(path)
    elif path.lower().endswith(".docx"):
        return parse_docx(path)
    else:
        raise ValueError("Unsupported file type")

