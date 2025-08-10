# qa_gen.py
from summarizer import model, tok, summarize
def gen_questions(missing_clause):
    prompt = f"Generate 3 concise questions to ask the counterparty because the contract is missing or weak on: {missing_clause}."
    inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=256)
    out = model.generate(**inputs, max_new_tokens=120)
    return tok.decode(out[0], skip_special_tokens=True)

if __name__ == "__main__":
    print(gen_questions("limitation of liability"))
