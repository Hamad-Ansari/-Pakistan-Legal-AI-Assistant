"""
Pakistan Legal AI Assistant — Main Streamlit App
Run with: streamlit run app.py
"""

import streamlit as st
from pathlib import Path

import config
from rag_engine import build_vector_store, retrieve_context
from llm_handler import check_ollama_connection, stream_response
from utils import detect_language, format_sources, has_devanagari

# ─────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — dark-friendly, professional look
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Main container */
.main .block-container { max-width: 780px; padding-top: 1.5rem; }

/* Header card */
.header-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.08);
}
.header-card h1 { color: #e8f4f8; margin: 0; font-size: 1.6rem; }
.header-card p  { color: #94a3b8; margin: 0.4rem 0 0; font-size: 1rem; }

/* Chat messages */
.user-bubble {
    background: #1e3a5f;
    border-radius: 14px 14px 4px 14px;
    padding: 0.9rem 1.1rem;
    margin: 0.6rem 0;
    color: #e2eaf4;
    max-width: 88%;
    margin-left: auto;
    font-size: 0.95rem;
}
.assistant-bubble {
    background: #0f2438;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px 14px 14px 4px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
    color: #dce9f5;
    max-width: 92%;
    font-size: 0.95rem;
    line-height: 1.7;
}

/* Disclaimer */
.disclaimer {
    background: rgba(234,179,8,0.08);
    border-left: 3px solid #ca8a04;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 0.9rem;
    margin-top: 0.8rem;
    font-size: 0.8rem;
    color: #fbbf24;
}

/* Source badge */
.source-badge {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    font-size: 0.75rem;
    color: #a5b4fc;
    margin-top: 0.6rem;
    display: inline-block;
}

/* Status indicators */
.status-ok   { color: #4ade80; font-size: 0.82rem; }
.status-fail { color: #f87171; font-size: 0.82rem; }

/* Example question pills */
.example-pill {
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    margin: 0.2rem;
    font-size: 0.8rem;
    color: #94a3b8;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "vs_loaded" not in st.session_state:
    st.session_state.vs_loaded = False


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Pakistan Legal AI")
    st.markdown("---")

    # Ollama status
    ollama_ok, available_models = check_ollama_connection()
    if ollama_ok:
        st.markdown(f'<p class="status-ok">● Ollama Connected</p>', unsafe_allow_html=True)
        if available_models:
            selected_model = st.selectbox(
                "Model", available_models,
                index=available_models.index(config.LLM_MODEL) if config.LLM_MODEL in available_models else 0
            )
            config.LLM_MODEL = selected_model
    else:
        st.markdown('<p class="status-fail">● Ollama Offline</p>', unsafe_allow_html=True)
        st.warning("Run `ollama serve` in terminal.")

    st.markdown("---")

    # Vector store management
    st.markdown("### 📚 Law Database")

    laws_path = Path(config.LAWS_DIR)
    pdf_files = list(laws_path.glob("*.pdf")) if laws_path.exists() else []

    if pdf_files:
        st.success(f"{len(pdf_files)} law PDF(s) found")
        for f in pdf_files:
            st.caption(f"• {f.stem.replace('_', ' ').title()}")
    else:
        st.info("Add PDF files to `data/laws/` folder to enable RAG.")
        st.caption("Example: pakistan_penal_code.pdf")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Build Index", use_container_width=True):
            with st.spinner("Building vector store..."):
                vs = build_vector_store(force_rebuild=True)
                if vs:
                    st.session_state.vector_store = vs
                    st.session_state.vs_loaded = True
                    st.success("Index ready!")
                else:
                    st.error("No PDFs found.")
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Vector store status
    vs_path = Path(config.VECTOR_STORE_DIR) / "index.faiss"
    if vs_path.exists():
        st.markdown('<p class="status-ok">● Vector store ready</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-fail">● No index built yet</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption("AI-powered legal guidance for Pakistan. Supports Urdu + English. Runs fully offline.")
    st.caption(f"Model: `{config.LLM_MODEL}`")
    st.caption(f"Embeddings: `all-MiniLM-L6-v2`")


# ─────────────────────────────────────────────────────────────────────────────
# Load vector store on startup (if index exists)
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.vs_loaded:
    vs_path = Path(config.VECTOR_STORE_DIR) / "index.faiss"
    if vs_path.exists():
        with st.spinner("Loading law database..."):
            st.session_state.vector_store = build_vector_store(force_rebuild=False)
            st.session_state.vs_loaded = True


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-card">
    <h1>⚖️ Pakistan Legal AI Assistant</h1>
    <p>قانونی رہنمائی — آپ کی اپنی زبان میں &nbsp;|&nbsp; Legal guidance in your own language</p>
</div>
""", unsafe_allow_html=True)

# Example questions (only show when chat is empty)
if not st.session_state.messages:
    st.markdown("#### 💡 Try asking:")
    examples = [
        "میرے مالک نے بغیر نوٹس کے گھر خالی کرنے کو کہا — میرے کیا حقوق ہیں؟",
        "My employer hasn't paid my salary for 2 months. What can I do?",
        "پولیس نے بغیر وارنٹ گھر تلاشی لی — کیا یہ قانونی ہے؟",
        "What is the process to file an FIR in Pakistan?",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": ex})
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Chat history display
# ─────────────────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-bubble">⚖️ {msg["content"]}</div>', unsafe_allow_html=True)
        if msg.get("sources"):
            st.markdown(f'<span class="source-badge">{msg["sources"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="disclaimer">{config.DISCLAIMER}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Chat input
# ─────────────────────────────────────────────────────────────────────────────
if not ollama_ok:
    st.error("⚠️ Ollama is not running. Please start it with `ollama serve` in your terminal.")

query = st.chat_input(
    "اپنا قانونی سوال یہاں لکھیں... / Ask your legal question here...",
    disabled=not ollama_ok,
)

if query and query.strip():
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query.strip()})
    st.markdown(f'<div class="user-bubble">🧑 {query.strip()}</div>', unsafe_allow_html=True)

    # Detect language BEFORE calling LLM
    lang = detect_language(query.strip())

    # Retrieve context from vector store
    context, source_docs = "", []
    if st.session_state.vector_store:
        context, source_docs = retrieve_context(query.strip(), st.session_state.vector_store)
    source_text = format_sources(source_docs)

    # Stream LLM response — pass detected language
    with st.empty():
        full_response = ""
        response_placeholder = st.empty()

        for chunk in stream_response(query.strip(), context, language=lang):
            full_response += chunk
            response_placeholder.markdown(
                f'<div class="assistant-bubble">⚖️ {full_response}▌</div>',
                unsafe_allow_html=True,
            )

        # Final render without cursor
        response_placeholder.markdown(
            f'<div class="assistant-bubble">⚖️ {full_response}</div>',
            unsafe_allow_html=True,
        )

    # Quality check — warn if Hindi script slipped into Urdu response
    if lang == "urdu" and has_devanagari(full_response):
        st.warning(
            "⚠️ ماڈل نے ہندی حروف استعمال کیے — بہتر نتائج کے لیے sidebar سے gemma2:2b منتخب کریں۔",
            icon="🔤"
        )

    if source_text:
        st.markdown(f'<span class="source-badge">{source_text}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer">{config.DISCLAIMER}</div>', unsafe_allow_html=True)

    # Save to session
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "sources": source_text,
    })