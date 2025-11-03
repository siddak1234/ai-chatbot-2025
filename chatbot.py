# chatbot.py
"""
AI Chatbot 2025 — Rule-based + OpenAI Fallback

- Responds to simple phrases using local logic
- Falls back to OpenAI for anything else
- Loads your API key from .env
"""

import os
import re
from datetime import datetime
from random import choice
from typing import List, Dict
from dotenv import load_dotenv

# ---- Load environment variables ----
load_dotenv()
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🤖 Welcome to AI Chatbot 2025!")
print("Type 'bye' to exit. Type '/ai <prompt>' to ask directly.\n")

# ---- Memory ----
state = {"user_name": None}

# ---- Local responses ----
def extract_name(text):
    m = re.search(r"\b(my name is|i am|i'm)\s+([A-Za-z][A-Za-z\-']+)", text)
    return m.group(2).capitalize() if m else None

def handle_greet():
    if state["user_name"]:
        return f"Hello {state['user_name']}! Great to see you."
    return choice(["Hello there!", "Hi! 👋", "Hey!"])

def handle_status():
    return "I'm just a bunch of code, but I'm running great 😄"

def handle_name(text):
    name = extract_name(text)
    if name:
        state["user_name"] = name
        return f"Nice to meet you, {name}! I'll remember your name."
    return "I'm AI Chatbot 2025, your Python-powered assistant."

def handle_time():
    return f"It's {datetime.now().strftime('%A %I:%M %p')}."

def handle_joke():
    jokes = [
        "Why did the developer go broke? Because they used up all their cache.",
        "I told my computer I needed a break, and it said: 'No problem — I'll go to sleep.'",
        "There are 10 kinds of people: those who understand binary and those who don't."
    ]
    return choice(jokes)

def handle_help():
    return (
        "Try these:\n"
        "- 'hello' / 'hi'\n"
        "- 'how are you'\n"
        "- 'my name is <Name>'\n"
        "- 'time'\n"
        "- 'tell me a joke'\n"
        "- '/ai <question>' for full AI mode\n"
        "- 'bye' to exit"
    )

def local_reply(text):
    t = text.lower().strip()
    if any(k in t for k in ("hello", "hi", "hey")):
        return handle_greet()
    if "how are you" in t:
        return handle_status()
    if "your name" in t or t == "name":
        return handle_name(t)
    if "my name is" in t:
        return handle_name(t)
    if "time" in t:
        return handle_time()
    if "joke" in t:
        return handle_joke()
    if t == "help":
        return handle_help()
    return None

# ---- OpenAI Chat fallback ----
def openai_chat(messages: List[Dict[str, str]]):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error using OpenAI: {e}"

# ---- Main Chat Loop ----
history = [{"role": "system", "content": "You are a helpful terminal chatbot."}]

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"bye", "exit", "quit"}:
        print("Bot: Goodbye! 👋")
        break

    # Force AI mode manually
    if user_input.startswith("/ai"):
        prompt = user_input[3:].strip()
        history.append({"role": "user", "content": prompt})
        reply = openai_chat(history)
        print(f"Bot: {reply}")
        history.append({"role": "assistant", "content": reply})
        continue

    # Try local logic first
    local = local_reply(user_input)
    if local:
        print(f"Bot: {local}")
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": local})
        continue

    # Otherwise, ask OpenAI
    print("Bot: 🤔 Let me think...")
    history.append({"role": "user", "content": user_input})
    reply = openai_chat(history)
    print(f"Bot: {reply}")
    history.append({"role": "assistant", "content": reply})
