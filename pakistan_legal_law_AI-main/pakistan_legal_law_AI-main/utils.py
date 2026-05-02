"""
Utility helpers — language detection, script validation, text cleaning.
"""

import re


def detect_language(text: str) -> str:
    """
    Returns 'urdu' if Urdu/Arabic script characters dominate,
    otherwise 'english'.
    Hindi (Devanagari) chars are treated as English trigger.
    """
    urdu_pattern = re.compile(
        r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"
    )
    devanagari_pattern = re.compile(r"[\u0900-\u097F]")

    urdu_chars = len(urdu_pattern.findall(text))
    hindi_chars = len(devanagari_pattern.findall(text))

    if hindi_chars > 0:
        return "english"

    return "urdu" if urdu_chars > 2 else "english"


def has_devanagari(text: str) -> bool:
    """Check if LLM response contains Hindi/Devanagari script (quality check)."""
    return bool(re.search(r"[\u0900-\u097F]", text))


def clean_text(text: str) -> str:
    """Remove excessive whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def format_sources(docs: list) -> str:
    """Format retrieved document sources for display."""
    if not docs:
        return ""
    sources = set()
    for doc in docs:
        src = doc.metadata.get("source", "")
        if src:
            sources.add(
                src.split("/")[-1].replace("_", " ").replace(".pdf", "").title()
            )
    if sources:
        return "📚 Sources: " + " | ".join(sorted(sources))
    return ""