# chatbot/llm.py
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()  # local dev only; in Docker you pass env vars with -e

MODE = os.getenv("LLM_MODE", "live").lower()  # "mock" or "live"
DRY_RUN = os.getenv("LLM_DRY_RUN", "").lower() in {"1", "true", "yes"}

_client = None  # lazy-initialized when needed


def _get_client():
    """Create the OpenAI client only in live mode, and only when needed."""
    global _client
    if _client is not None:
        return _client
    if MODE != "live":
        return None
    from openai import OpenAI  # import here to avoid requiring the package in mock mode
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required in live mode.")
    _client = OpenAI(api_key=api_key)
    return _client


def _mock_reply(messages: List[Dict[str, str]]) -> str:
    """Simple deterministic mock for development."""
    last_user: Optional[str] = None
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = m.get("content", "")
            break
    if DRY_RUN:
        print("[LLM_DRY_RUN] Would send:", {"messages": messages[-3:]})
    return "[mock] You said: " + (last_user or "(no user message)")


def chat(messages: List[Dict[str, str]], temperature: float = 0.7, model: str = "gpt-4o-mini") -> str:
    """Return assistant text. Uses mock in dev or OpenAI in live."""
    if MODE == "mock":
        return _mock_reply(messages)

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[llm-error] {e}"
