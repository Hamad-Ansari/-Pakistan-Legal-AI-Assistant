# ⚖️ QanoonGPT

### Pakistan’s Offline AI Legal Assistant (Urdu + English)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Offline AI](https://img.shields.io/badge/Offline-AI-green)
![Urdu](https://img.shields.io/badge/Language-Urdu%20%2B%20English-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🇵🇰 Overview

**QanoonGPT** is an AI-powered bilingual legal assistant built for Pakistan.  
It helps users understand laws, legal procedures, and legal documents in **Urdu + English**.

✅ Works fully offline  
✅ Supports PDF law books  
✅ Fast local AI using Ollama  
✅ RAG-based legal search  
✅ Runs on 8GB RAM laptops

---

## ✨ Features

- 💬 Legal Chatbot in Urdu + English  
- 📚 Upload Pakistani law PDFs  
- 🔍 Smart legal search with citations  
- 🔒 100% private local inference  
- ⚡ Fast Streamlit dashboard  
- 🧠 Uses local LLMs (Llama / Gemma)

---

## 🏗️ Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | Streamlit |
| Backend | Python |
| AI Models | Ollama |
| Search | FAISS |
| Embeddings | Sentence Transformers |
| Documents | PDF Parser |

---

## ⚙️ Installation

```bash
git clone https://github.com/yourname/QanoonGPT.git
cd QanoonGPT
pip install -r requirements.txt
ollama serve
ollama pull llama3.2:1b
streamlit run app.py
