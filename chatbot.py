# chatbot.py
"""
AI Chatbot 2025 — Rule-based + OpenAI (streaming) with persistence

Features
- Fast local intents (greet, status, name, time, joke, help)
- OpenAI fallback with LIVE streaming (ChatGPT-style)
- Remembers your name across runs (state.json)
- Caps conversation history to control cost

Setup
1) pip install openai python-dotenv
2) .env -> OPENAI_API_KEY=sk-...
3) .gitignore -> .env, state.json, .venv/, __pycache__/
"""

import os
import re
import json
from datetime import datetime
from random import choice
from typing import List, Dict, Optional

from dotenv import load_dotenv

# ---------- ENV & CLIENT ----------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None

# ---------- STATE (PERSISTENCE) ----------
STATE_FILE = "state.json"

def load_state() -> Dict[str, Optional[str]]:
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "user_name" in data:
                return {"user_name": data.get("user_name")}
    except Exception:
        pass
    return {"user_name": None}

def save_state(state: Dict[str, Optional[str]]) -> None:
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

state = load_state()

# ---------- HELPERS: LOCAL INTENTS ----------
def extract_name(text: str) -> Optional[str]:
    """
    Match 'my name is Alex', 'i am Sam', "i'm Priya"
    """
    m = re.search(r"\b(my name is|i am|i'm)\s+([A-Za-z][A-Za-z\-']+)", text, flags=re.IGNORECASE)
    return m.group(2).strip().capitalize() if m else None

def handle_greet() -> str:
    if state["user_name"]:
        return f"Hello {state['user_name']}! Great to see you."
    return choice(["Hello there!", "Hi! 👋", "Hey!"])

def handle_status() -> str:
    return "I'm just a bunch of code, but I'm running great 😄"

def handle_thanks() -> str:
    return "You're Welcome! 😄"

def handle_name(text: str) -> str:
    name = extract_name(text)
    if name:
        state["user_name"] = name
        save_state(state)
        return f"Nice to meet you, {name}! I'll remember your name."
    return "I'm AI Chatbot 2025, your Python-powered assistant."

def handle_time() -> str:
    return f"It's {datetime.now().strftime('%A %I:%M %p')}."

def handle_joke() -> str:
    jokes = [
        "Why did the developer go broke? Because they used up all their cache.",
        "I told my computer I needed a break, and it said: 'No problem — I'll go to sleep.'",
        "There are 10 kinds of people: those who understand binary and those who don't."
    ]
    return choice(jokes)

def handle_help() -> str:
    return (
        "Try these:\n"
        "- 'hello' / 'hi'\n"
        "- 'how are you'\n"
        "- 'my name is <Name>'\n"
        "- 'time'\n"
        "- 'tell me a joke'\n"
        "- '/ai <question>' for full AI mode\n"
        "- '/clear' to reset memory\n"
        "- 'bye' to exit"
    )

def local_reply(text: str) -> Optional[str]:
    t = text.lower().strip()
    if any(k in t for k in ("hello", "hi", "hey")):
        return handle_greet()
    if "how are you" in t:
        return handle_status()
    if "your name" in t or t == "name":
        return handle_name(t)
    if "my name is" in t:
        return handle_name(t)
    if "time" in t or "what time" in t:
        return handle_time()
    if "joke" in t or "make me laugh" in t:
        return handle_joke()
    if t == "help":
        return handle_help()
    if t == "thanks" or t == "thank you":
        return handle_thanks()
    if t == "/clear":
        state["user_name"] = None
        save_state(state)
        return "Cleared memory. I won't remember your name until you tell me again."
    return None

# ---------- HISTORY MANAGEMENT ----------
def capped(messages: List[Dict[str, str]], max_pairs: int = 12) -> List[Dict[str, str]]:
    """
    Keep system + last N user/assistant pairs to bound context size.
    """
    if not messages:
        return messages
    sys = messages[:1] if messages[0].get("role") == "system" else []
    rest = messages[1:] if sys else messages
    return sys + rest[-(max_pairs * 2):]

# ---------- OPENAI HELPERS ----------
def openai_stream(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    """
    Stream tokens to the console as they arrive; return full text at the end.
    """
    if client is None:
        return "OpenAI is not configured. Set OPENAI_API_KEY in your .env."

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=capped(messages),
            temperature=temperature,
            stream=True,
        )
        full = []
        print("Bot: ", end="", flush=True)
        for chunk in stream:
            # For Chat Completions streaming, text arrives in choices[0].delta.content
            delta = getattr(chunk.choices[0], "delta", None)
            piece = getattr(delta, "content", None) if delta else None
            if piece:
                print(piece, end="", flush=True)
                full.append(piece)
        print()  # newline after completion
        return "".join(full) if full else "(no content)"
    except Exception as e:
        return f"Error (stream): {e}"

def openai_chat(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    """
    Non-streaming fallback (kept around for simplicity/tests).
    """
    if client is None:
        return "OpenAI is not configured. Set OPENAI_API_KEY in your .env."

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=capped(messages),
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error using OpenAI: {e}"

# ---------- BANNER ----------
print("🤖 Welcome to AI Chatbot 2025!")
if client is None:
    print("ℹ️  No OPENAI_API_KEY found — local replies will work; AI answers will show a warning.")
print("Type 'bye' to exit. Type '/ai <prompt>' to ask directly. Type 'help' for options.\n")

# ---------- MAIN LOOP ----------
history: List[Dict[str, str]] = [
    {"role": "system", "content": "You are a helpful, concise terminal chatbot."}
]

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        save_state(state)
        print("\nBot: Goodbye! 👋")
        break

    if user_input.lower() in {"bye", "exit", "quit"}:
        save_state(state)
        print("Bot: Goodbye! 👋")
        break

    # Force LLM directly: /ai <prompt>
    if user_input.startswith("/ai"):
        prompt = user_input[3:].strip() or "Please respond helpfully to the user."
        history.append({"role": "user", "content": prompt})
        reply = openai_stream(history)
        history.append({"role": "assistant", "content": reply})
        continue

    # Try local rules first
    local = local_reply(user_input)
    if local is not None:
        print(f"Bot: {local}")
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": local})
        continue

    # Otherwise, LLM with streaming
    print("Bot: 🤔 Let me think...")
    history.append({"role": "user", "content": user_input})
    reply = openai_stream(history)
    history.append({"role": "assistant", "content": reply})
