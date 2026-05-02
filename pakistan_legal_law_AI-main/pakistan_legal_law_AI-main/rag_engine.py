"""
RAG Engine — builds and queries the FAISS vector store from law PDFs.
"""

import os
import pickle
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config


def _get_embeddings():
    """Load the embedding model (cached after first call)."""
    return HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_store(force_rebuild: bool = False) -> FAISS:
    """
    Load PDFs from LAWS_DIR, chunk them, embed, and save a FAISS index.
    Returns the loaded vector store.
    """
    index_path = Path(config.VECTOR_STORE_DIR)
    index_file = index_path / "index.faiss"

    # Return cached store if it exists and rebuild not forced
    if index_file.exists() and not force_rebuild:
        return _load_vector_store()

    laws_path = Path(config.LAWS_DIR)
    if not laws_path.exists() or not any(laws_path.glob("*.pdf")):
        return None  # No PDFs yet — app will show a warning

    # Load all PDFs
    loader = DirectoryLoader(
        str(laws_path),
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    documents = loader.load()

    if not documents:
        return None

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "۔", ".", " "],
    )
    chunks = splitter.split_documents(documents)

    # Build and save FAISS index
    embeddings = _get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    index_path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(index_path))

    return vector_store


def _load_vector_store() -> FAISS:
    """Load existing FAISS index from disk."""
    embeddings = _get_embeddings()
    return FAISS.load_local(
        config.VECTOR_STORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve_context(query: str, vector_store: FAISS) -> tuple[str, list]:
    """
    Retrieve top-K relevant law chunks for a query.
    Returns (context_string, source_docs).
    """
    if vector_store is None:
        return "", []

    docs = vector_store.similarity_search(query, k=config.TOP_K_RESULTS)
    context = "\n\n---\n\n".join(doc.page_content for doc in docs)
    return context, docs
