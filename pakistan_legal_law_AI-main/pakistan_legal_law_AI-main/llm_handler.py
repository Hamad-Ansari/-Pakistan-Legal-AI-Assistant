"""
LLM Handler — talks to Ollama (local models like llama3.2:1b / gemma2:2b).
Language-aware: sends Urdu or English system prompt based on detected language.
"""

import requests
import json
from typing import Generator

import config


def check_ollama_connection() -> tuple[bool, list[str]]:
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            return True, models
        return False, []
    except Exception:
        return False, []


def stream_response(query: str, context: str, language: str = "english") -> Generator[str, None, None]:
    """
    language: "urdu" | "english" — picks the correct system prompt.
    Small models need separate prompts per language — conditional instructions confuse them.
    """
    if language == "urdu":
        fallback_ctx = "کوئی مخصوص قانونی حوالہ نہیں ملا۔ عمومی رہنمائی دیں۔"
        template = config.SYSTEM_PROMPT_URDU
    else:
        fallback_ctx = "No specific law context found. Give general guidance."
        template = config.SYSTEM_PROMPT_ENGLISH

    ctx = context if context else fallback_ctx
    prompt = template.format(context=ctx)

    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_predict": 900,
            "top_p": 0.85,
            "repeat_penalty": 1.1,
        },
    }

    try:
        with requests.post(
            f"{config.OLLAMA_BASE_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
    except requests.exceptions.ConnectionError:
        yield "\n\n❌ **Ollama Connection Error**\n\nPlease make sure Ollama is running:\n```\nollama serve\n```"
    except requests.exceptions.Timeout:
        yield "\n\n⏱️ **Response timed out.** Try a shorter question or restart Ollama."
    except Exception as e:
        yield f"\n\n❌ **Error:** {str(e)}"