import gradio as gr
import pandas as pd
from datetime import datetime
from scripts.parse_docs import parse_file
from scripts.embed_index import find_clauses_from_text
from scripts.summarizer import summarize_text
from data.rules_check import run_checks
from fpdf import FPDF
import mimetypes

# --- New: Suggest questions/improvements ---
def suggest_questions_and_improvements(flags, clauses):
    questions = []
    improvements = []
    for f in flags:
        if not f.get("present"):
            questions.append(f"What is your position on: {f.get('desc')}?")
            improvements.append(f"Consider adding: {f.get('desc')}")
    for c in clauses:
        for m in c.get("matches", []):
            if m.get("score", 1.0) < 0.7:
                improvements.append(f"Review clause: {m['clause_type']} (score low: {m['score']:.2f})")
    return "\n".join(f"- {q}" for q in questions) or "No questions.", "\n".join(f"- {i}" for i in improvements) or "No suggestions."

# Report generator (unchanged)
def make_pdf_report(summary, clauses, flags, out_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, sanitize_for_pdf("Contract Summary\n\n"))
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, sanitize_for_pdf(summary or "No summary."))
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0,6, sanitize_for_pdf("Detected Clauses:\n"))
    pdf.set_font("Arial", size=10)
    for i, c in enumerate(clauses):
        chunk_text = sanitize_for_pdf(c.get('chunk', '')[:300].replace('\n', ' '))
        pdf.multi_cell(0, 5, f"{i+1}. {chunk_text}")
        for m in c.get("matches", []):
            pdf.multi_cell(0,5, sanitize_for_pdf(f"    - {m['clause_type']} (score: {m['score']:.2f})"))
        pdf.ln(1)
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0,6, sanitize_for_pdf("Flags:\n"))
    pdf.set_font("Arial", size=10)
    for f in flags:
        present = "Yes" if f.get("present") else "No"
        pdf.multi_cell(0,5, sanitize_for_pdf(f"- {f.get('desc')} : {present}"))
    pdf.output(out_path)

# Main pipeline
def analyze_file(file):
    if file is None:
        return "No file uploaded.", pd.DataFrame(), pd.DataFrame(), None, "", ""
    path = file.name

    # --- File type validation ---
    mime, _ = mimetypes.guess_type(path)
    if not (mime and (mime.startswith("application/pdf") or mime in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"])):
        return (
            "❌ Unsupported file type. Please upload a valid PDF or DOCX.",
            pd.DataFrame(), pd.DataFrame(), None, "", ""
        )

    try:
        text = parse_file(path)
    except Exception as e:
        return (
            f"❌ Failed to parse file: {str(e)}",
            pd.DataFrame(), pd.DataFrame(), None, "", ""
        )

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

    # New: Generate questions/improvements
    questions, improvements = suggest_questions_and_improvements(flags, clauses)

    # Create a PDF report file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_pdf = f"report_{ts}.pdf"
    make_pdf_report(summary, clauses, flags, out_pdf)

    md_summary = (
        "<h3>Contract summary (auto-generated)</h3>"
        f"{summary or 'No summary generated.'}"
    )
    return md_summary, clauses_df, flags_df, out_pdf, questions, improvements

def sanitize_for_pdf(text):
    # Replace common Unicode bullets and dashes with ASCII equivalents
    return (
        text.replace("•", "-")
            .replace("–", "-")
            .replace("—", "-")
            .replace("“", '"')
            .replace("”", '"')
            .replace("’", "'")
            .replace("‘", "'")
            .encode("latin-1", "replace")
            .decode("latin-1")
    )

custom_css = """
body, #root, .gradio-container {
    background: #f5f6fa !important;
    color: #222 !important;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
#main-card {
    display: flex;
    flex-direction: column;
    gap: 28px;
    align-items: stretch;
    background: transparent;
    border-radius: 18px;
    box-shadow: none;
    padding: 32px 0;
    min-height: 100vh;
    width: 100%;
    margin: 0 auto;
}
#sidebar {
    min-width: 320px !important;
    max-width: 340px !important;
    background: #f0f1f5 !important;
    color: #222 !important;
    font-size: 1.08rem;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    border-top-right-radius: 18px;
    border-bottom-right-radius: 18px;
    box-shadow: 2px 0 12px #0001;
    padding-top: 32px;
}
#sidebar h1, #sidebar * {
    color: #222 !important;
    background: transparent !important;
}
#sidebar .gr-button, #sidebar .gr-file {
    background: #2563eb !important;
    color: #fff !important;
    border-radius: 8px !important;
    border: none !important;
    margin-bottom: 12px;
    font-weight: 600;
    transition: background 0.2s;
}
#sidebar #analyze-btn, #sidebar #close-btn {
    background: #2563eb !important;
    color: #fff !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600;
    transition: background 0.2s;
}
#sidebar .gr-button:hover, #sidebar .gr-file:hover, #sidebar #analyze-btn:hover, #sidebar #close-btn:hover {
    background: #3b82f6 !important;
    color: #fff !important;
}
.card-section, #summary-box, #summary-box * {
    background: #fff !important;
    color: #222 !important;
    border-radius: 14px;
    box-shadow: 0 8px 32px #0002; /* Increased shadow */
    padding: 28px 28px 20px 28px;
    margin-bottom: 0;
    border-left: none;
    transition: box-shadow 0.2s;
    width: 100%;
    box-sizing: border-box;
    font-size: 1.12rem;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    line-height: 1.7;
}
.card-section:hover {
    box-shadow: 0 12px 48px #0003;
}
.card-header {
    font-size: 1.22rem;
    font-weight: 700;
    color: #222 !important;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
#summary-box h3 {
    font-size: 1.3rem;
    font-weight: 800;
    color: #222 !important;
    margin-bottom: 18px;
    margin-top: 0;
    letter-spacing: 0.01em;
}
#clauses-table, #flags-table {
    max-width: 100%;
    width: 100%;
    overflow-x: auto;
    box-sizing: border-box;
    color: #222 !important;
    background: #fff !important;
    border-radius: 8px;
    font-size: 1.05rem;
}
"""

title = "🧑‍⚖️ AgentForce Legal Contract Assistant"
desc = (
    "<b>Accelerate contract review with AI.</b><br>"
    "Upload a contract (PDF/DOCX). The assistant will extract, summarize, flag, and suggest improvements.<br><br>"
    "<ul>"
    "<li><b>Clause Extraction</b>: Instantly see key terms</li>"
    "<li><b>Compliance Check</b>: Find missing/risky clauses</li>"
    "<li><b>Negotiation Prep</b>: Get questions & improvements</li>"
    "<li><b>PDF Report</b>: Download a professional summary</li>"
    "</ul>"
    "<small>All processing is local. No data is stored.</small>"
)

with gr.Blocks(css=custom_css, title=title, theme=gr.themes.Soft()) as iface:
    with gr.Row():
        # Sidebar (left)
        with gr.Column(scale=1, elem_id="sidebar"):
            gr.Markdown(f"<h1 style='color:#111;'>AgentForce Legal</h1>")
            gr.Markdown(desc)
            file_input = gr.File(label="Upload Contract (PDF or DOCX)", file_types=[".pdf", ".docx"])
            submit_btn = gr.Button("Analyze Contract", elem_id="analyze-btn", variant="primary")
            close_btn = gr.Button("Close", elem_id="close-btn")
        # Main content (right)
        with gr.Column(scale=2, elem_id="main-card"):
            welcome_card = gr.Markdown(
                """
                <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:60vh;'>
                    <img src='https://img.icons8.com/ios-filled/100/3b82f6/agreement.png' width='80' style='margin-bottom:24px;'/>
                    <h2 style='color:#111;'>Welcome to AgentForce Legal</h2>
                    <p style='font-size:1.1rem;color:#222b;max-width:500px;text-align:center;'>
                        Upload a contract to get instant AI-powered clause extraction, compliance checks, negotiation suggestions, and a professional PDF report.
                    </p>
                </div>
                """,
                elem_id="welcome-card",
                visible=True
            )
          
            # 2. Detected Clauses
            clauses_header = gr.Markdown("<span class='card-header'>🧩 Detected Clauses</span>", elem_id="clauses-header", visible=False, elem_classes=["card-section"])
            clauses = gr.Dataframe(label=None, elem_id="clauses-table", visible=False, elem_classes=["card-section"])
            # 3. Compliance Flags
            flags_header = gr.Markdown("<span class='card-header'>🛡️ Compliance Flags</span>", elem_id="flags-header", visible=False, elem_classes=["card-section"])
            flags = gr.Dataframe(label=None, elem_id="flags-table", visible=False, elem_classes=["card-section"])
            # 4. Suggested Questions
            questions_header = gr.Markdown("<span class='card-header'>❓ Suggested Questions</span>", elem_id="questions-header", visible=False, elem_classes=["card-section"])
            questions = gr.Textbox(label=None, lines=4, interactive=False, elem_id="questions-card", visible=False, elem_classes=["card-section"])
            # 5. Clause Improvements
            improvements_header = gr.Markdown("<span class='card-header'>📝 Clause Improvements</span>", elem_id="improvements-header", visible=False, elem_classes=["card-section"])
            improvements = gr.Textbox(label=None, lines=4, interactive=False, elem_id="improvements-card", visible=False, elem_classes=["card-section"])
            # 6. Download PDF Report
            pdf_header = gr.Markdown("<span class='card-header'>📥 Download PDF Report</span>", elem_id="pdf-header", visible=False, elem_classes=["card-section"])
            pdf_out = gr.File(label=None, elem_id="pdf-link", visible=False, elem_classes=["card-section"])

    def analyze_and_show(file):
        md_summary, clauses_df, flags_df, out_pdf, questions_text, improvements_text = analyze_file(file)
        show = file is not None
        return (
            gr.update(visible=not show),  # Hide welcome card after analysis
            gr.update(value=md_summary, visible=show),
            gr.update(visible=show),  # Detected Clauses header
            gr.update(value=clauses_df, visible=show),
            gr.update(visible=show),  # Compliance Flags header
            gr.update(value=flags_df, visible=show),
            gr.update(visible=show),  # Suggested Questions header
            gr.update(value=questions_text, visible=show),
            gr.update(visible=show),  # Clause Improvements header
            gr.update(value=improvements_text, visible=show),
            gr.update(visible=show),  # PDF header
            gr.update(value=out_pdf, visible=show)
        )

    submit_btn.click(
        analyze_and_show,
        inputs=file_input,
        outputs=[
            welcome_card,
            clauses_header,
            clauses,
            flags_header,
            flags,
            questions_header,
            questions,
            improvements_header,
            improvements,
            pdf_header,
            pdf_out
        ]
    )

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
