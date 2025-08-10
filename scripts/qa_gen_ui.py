import gradio as gr
from qa_gen import gen_questions

def generate_questions_ui(missing_clause):
    return gen_questions(missing_clause)

with gr.Blocks(title="Legal Contract QA Generator") as demo:
    gr.Markdown("# Legal Contract QA Generator\nEnter a missing or weak clause to generate questions for the counterparty.")
    with gr.Row():
        clause_input = gr.Textbox(label="Missing/Weak Clause", placeholder="e.g. limitation of liability")
    with gr.Row():
        output = gr.Textbox(label="Generated Questions", lines=6)
    generate_btn = gr.Button("Generate Questions")
    generate_btn.click(fn=generate_questions_ui, inputs=clause_input, outputs=output)

demo.launch()
