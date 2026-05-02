# ⚖️ Pakistan Legal AI Assistant

AI-powered bilingual (Urdu + English) legal guidance — runs fully offline on 8GB RAM.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama (separate terminal)
ollama serve

# 3. Pull your model (first time only)
ollama pull llama3.2:1b
# OR
ollama pull gemma2:2b

# 4. Add law PDFs
mkdir -p data/laws
# Copy your PDF files into data/laws/

# 5. Run the app
streamlit run app.py
```

## First Time Setup (in the app)
1. Open sidebar → click **"Build Index"** to process your PDFs
2. Wait for "Index ready!" confirmation
3. Start asking questions!

## Without PDFs
The app still works — LLM answers from general knowledge.
With PDFs — answers are grounded in actual Pakistani law texts.

## Recommended Models (8GB RAM)
| Model | RAM Usage | Speed | Quality |
|-------|-----------|-------|---------|
| llama3.2:1b | ~1.5 GB | Fast | Good |
| gemma2:2b | ~2.5 GB | Medium | Better |

## File Structure
```
pakistan-legal-ai/
├── app.py           # Streamlit UI
├── rag_engine.py    # FAISS vector store
├── llm_handler.py   # Ollama API calls
├── utils.py         # Language detection
├── config.py        # All settings
├── data/laws/       # Put PDFs here
└── vector_store/    # Auto-generated index
```