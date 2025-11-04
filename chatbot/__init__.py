# chatbot/__init__.py

__all__ = ["local_reply", "load_state", "save_state", "chat", "__version__"]
__version__ = "0.1.0"

# Re-export the main entry points
from .router import local_reply
from .state import load_state, save_state
from .llm import chat
