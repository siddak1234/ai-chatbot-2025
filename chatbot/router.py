import re
from datetime import datetime
from random import choice

def _extract_name(text: str):
    """
    Extracts a name from phrases like 'my name is Alex' or 'I'm Jordan'.
    Returns None if no name is found.
    """
    m = re.search(r"\b(my name is|i am|i'm)\s+([A-Za-z][A-Za-z\-']+)", text, flags=re.I)
    return m.group(2).strip().capitalize() if m else None


def local_reply(text: str, state: dict):
    """
    Determines how to respond based on text patterns.
    Uses the user's name if known (from state).
    Returns a string if it knows how to respond, or None if not.
    """
    t = text.lower().strip()

    # 1. Greetings
    if any(k in t for k in ("hello", "hi", "hey")):
        return f"Hello {state['user_name']}! Great to see you." if state.get("user_name") \
               else choice(["Hello there!", "Hi! 👋", "Hey!"])

    # 2. Check-in
    if "how are you" in t:
        return "I'm just a bunch of code, but I'm running great 😄"

    # 3. Asking for bot's name
    if "your name" in t or t == "name":
        return "I'm AI Chatbot 2025, your Python-powered assistant."

    # 4. Detecting user's name and saving it
    name = _extract_name(t)
    if name:
        state["user_name"] = name
        return f"Nice to meet you, {name}! I'll remember your name."

    # 5. Time queries
    if "time" in t or "what time" in t:
        return f"It's {datetime.now().strftime('%A %I:%M %p')}."

    # 6. Jokes
    if "joke" in t or "make me laugh" in t:
        jokes = [
            "Why did the developer go broke? Because they used up all their cache.",
            "I told my computer I needed a break, and it said: 'No problem — I'll go to sleep.'",
            "There are 10 kinds of people: those who understand binary and those who don't."
        ]
        return choice(jokes)

    # 7. Help command
    if t == "help":
        return "Try: hello, how are you, my name is <Name>, time, tell me a joke, /clear, /ai <prompt>, bye"

    # 8. Clear memory
    if t == "/clear":
        state["user_name"] = None
        return "Cleared memory. I won't remember your name until you tell me again."

    # 9. Unknown input — return None (so AI handles it)
    return None
