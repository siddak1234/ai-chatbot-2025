import json
from typing import Dict, Optional

# Where we persist small bits of memory (e.g., user_name)
STATE_FILE = "data/state.json"

def load_state() -> Dict[str, Optional[str]]:
    """
    Load the bot's memory from state.json.
    Returns a dict like {"user_name": "Alex"} or {"user_name": None}.
    If the file doesn't exist or is malformed, returns a default state.
    """
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "user_name" in data:
                return {"user_name": data.get("user_name")}
    except Exception:
        pass
    return {"user_name": None}

def save_state(state: Dict[str, Optional[str]]) -> None:
    """
    Write the bot's memory to state.json.
    This is intentionally tolerant: failures are ignored (no crash).
    """
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass
