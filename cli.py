# cli.py
"""
Terminal chat for AI-CHATBOT-2025
- Uses local rules first (router.local_reply)
- Falls back to OpenAI via chatbot.llm.chat
- Persists small memory in data/state.json
Commands:
  /ai <prompt>   force LLM
  /clear         forget saved name
  /help          show help
  /bye           exit
"""

from typing import List, Dict
from chatbot.state import load_state, save_state
from chatbot.router import local_reply
from chatbot.llm import chat as llm_chat


def main() -> None:
    print("🤖 Welcome to AI Chatbot 2025 (CLI)")
    print("Type /help for options.\n")

    # conversation memory for LLM calls
    history: List[Dict[str, str]] = [{"role": "system", "content": "You are a helpful terminal chatbot."}]
    state = load_state()

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye! 👋")
            break

        if not user:
            continue

        # exit
        if user.lower() in {"bye", "/bye", "quit", "exit"}:
            print("Bot: Goodbye! 👋")
            break

        # help
        if user.lower() in {"/help", "help"}:
            print("Bot: Try: hello • how are you • my name is <Name> • time • tell me a joke • /ai <q> • /clear • /bye")
            continue

        # clear memory
        if user.lower() == "/clear":
            state["user_name"] = None
            save_state(state)
            print("Bot: Cleared memory. I won't remember your name until you tell me again.")
            continue

        # force LLM
        if user.startswith("/ai"):
            prompt = user[3:].strip()
            if not prompt:
                print("Bot: Usage: /ai <your question>")
                continue
            history.append({"role": "user", "content": prompt})
            reply = llm_chat(history)
            print(f"Bot: {reply}")
            history.append({"role": "assistant", "content": reply})
            continue

        # try local rules
        local = local_reply(user, state)
        if local is not None:
            print(f"Bot: {local}")
            save_state(state)  # may update user_name
            history.append({"role": "user", "content": user})
            history.append({"role": "assistant", "content": local})
            continue

        # fallback to LLM
        print("Bot: 🤔 Let me think…")
        history.append({"role": "user", "content": user})
        reply = llm_chat(history)
        print(f"Bot: {reply}")
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
