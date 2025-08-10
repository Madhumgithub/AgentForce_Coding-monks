# 📝 Legal Document Summarizer & Clause Checker

An AI-powered legal contract assistant that:
- Summarizes contracts automatically
- Detects important clauses (payment, liability, confidentiality, termination, jurisdiction, etc.)
- Flags missing or risky clauses
- Generates downloadable PDF compliance reports

---

## 🚀 Features
- 📄 **Auto Contract Summary**
- 🔍 **Clause Detection**
- 🚩 **Risk Flags**
- 📑 **PDF Report Export**

---

## 📦 Installation

1. Clone this repository:
```bash
git clone https://github.com/Madhumgithub/AgentForce_Coding-monks.git
cd AgentForce_Coding-monks
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
python app.py
```

The app will start locally and show a URL in your terminal (e.g., `http://127.0.0.1:7860`).  
Open it in your browser to use the tool.

---

## 📂 Folder Structure
```
AgentForce_Coding-monks/
│
├── app.py                # Main Gradio app
├── requirements.txt      # All Python libraries
├── README.md             # Documentation
├── /models               # (Optional) Local models
├── /sample_contracts     # Example contracts for testing
├── /utils                # Helper scripts
└── /reports              # Generated PDF reports
```

---

## 📄 Example Output

- **Summary:**  
  AlphaTech Solutions ('Provider') and BetaCorp Industries ('Client')...  
- **Clauses Found:** Payment, Liability, Termination, Jurisdiction  
- **Flags:** Missing confidentiality, missing penalty clause, etc.  
- **Report:** Downloadable PDF

---

## 🌐 Deploy on Hugging Face Spaces

1. Push your repo to GitHub.  
2. Create a new Space on Hugging Face: https://huggingface.co/spaces  
3. Choose **Gradio** SDK.  
4. Connect your GitHub repo.  
5. Deploy – it’s live for anyone to use!

---

## 👥 Contributors
- Madhumgithub
- Team Coding Monks

---

## 📜 License
MIT License
