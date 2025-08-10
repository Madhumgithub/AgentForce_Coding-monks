# app.py
import gradio as gr
import pandas as pd
from datetime import datetime
from scripts.parse_docs import parse_file
from scripts.embed_index import find_clauses_from_text
from scripts.summarizer import summarize_text
from data.rules_check import run_checks
from fpdf import FPDF

# Report generator
def make_pdf_report(summary, clauses, flags, out_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, "Contract Summary\n\n")
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, summary or "No summary.")
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0,6, "Detected Clauses:\n")
    pdf.set_font("Arial", size=10)
    for i, c in enumerate(clauses):
        chunk_text = c.get('chunk', '')[:300].replace('\n', ' ')
        pdf.multi_cell(0, 5, f"{i+1}. {chunk_text}")
        for m in c.get("matches", []):
            pdf.multi_cell(0,5, f"    - {m['clause_type']} (score: {m['score']:.2f})")
        pdf.ln(1)
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0,6, "Flags:\n")
    pdf.set_font("Arial", size=10)
    for f in flags:
        present = "Yes" if f.get("present") else "No"
        pdf.multi_cell(0,5, f"- {f.get('desc')} : {present}")
    pdf.output(out_path)

# Main pipeline
def analyze_file(file):
    if file is None:
        return "No file uploaded.", pd.DataFrame(), pd.DataFrame(), None

    path = file.name
    text = parse_file(path)
    clauses = find_clauses_from_text(text)
    summary = summarize_text(text)
    flags = run_checks(text)

    # Prepare DataFrames
    clauses_df_rows = []
    for c in clauses:
        matches_str = "; ".join([f"{m['clause_type']} ({m['score']:.2f})" for m in c.get("matches",[])])
        clauses_df_rows.append({"chunk": c.get("chunk","")[:600], "matches": matches_str})
    clauses_df = pd.DataFrame(clauses_df_rows)

    flags_rows = []
    for f in flags:
        flags_rows.append({"check": f.get("desc"), "present": "✅" if f.get("present") else "❌"})
    flags_df = pd.DataFrame(flags_rows)

    # Create a PDF report file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_pdf = f"report_{ts}.pdf"
    make_pdf_report(summary, clauses, flags, out_pdf)

    md_summary = "### Contract summary (auto-generated)\n\n" + (summary or "No summary generated.")
    return md_summary, clauses_df, flags_df, out_pdf

title = "Legal Contract Summarizer & Validator — MVP"
desc = "Upload a contract (PDF/DOCX). The agent extracts key clauses, summarizes, flags missing/risky items and generates a PDF report."

iface = gr.Interface(
    fn=analyze_file,
    inputs = gr.File(type="filepath"),
    outputs=[
        gr.Markdown(label="Summary"),
        gr.Dataframe(label="Detected Clauses"),
        gr.Dataframe(label="Flags"),
        gr.File(label="Download PDF Report")
    ],
    title=title,
    description=desc
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
