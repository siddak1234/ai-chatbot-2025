# app/server.py
"""
AI Chatbot 2025 — FastAPI Backend
---------------------------------
This file exposes a REST API for your chatbot.

Endpoints:
- GET /healthz → Health check
- POST /chat   → Chat endpoint (local logic + OpenAI fallback)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import from your chatbot package
from chatbot.state import load_state, save_state
from chatbot.router import local_reply
from chatbot.llm import chat as llm_chat


# -------------------------------------------------
# 1️⃣ Create the FastAPI application
# -------------------------------------------------
app = FastAPI(
    title="AI Chatbot 2025 API",
    version="0.1.0",
    description="Backend API for AI Chatbot 2025 (Python + OpenAI)",
)

# -------------------------------------------------
# 2️⃣ Enable CORS (for iOS or web frontends)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # in production, restrict to your domain or app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# 3️⃣ Define Pydantic models for requests & responses
# -------------------------------------------------
class Msg(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Msg]        # conversation history
    text: str                  # latest user message


class ChatResponse(BaseModel):
    reply: str
    used_llm: bool             # False if handled locally, True if used OpenAI


# -------------------------------------------------
# 4️⃣ Define routes
# -------------------------------------------------
@app.get("/healthz")
def health_check():
    """Simple health endpoint to verify the server is alive."""
    return {"status": "ok", "version": "0.1.0"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Main chatbot route:
    1. Try rule-based logic first (fast, local).
    2. If no match, send to OpenAI via llm.py.
    3. Persist memory between chats using state.py.
    """
    # Load current memory
    state = load_state()

    # Step 1: Try local logic
    local = local_reply(req.text, state)
    if local is not None:
        save_state(state)
        return ChatResponse(reply=local, used_llm=False)

    # Step 2: Fallback to OpenAI
    messages = [m.model_dump() for m in req.messages]
    messages.append({"role": "user", "content": req.text})

    reply = llm_chat(messages)
    save_state(state)
    return ChatResponse(reply=reply, used_llm=True)


# -------------------------------------------------
# 5️⃣ (Optional) Root route
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to AI Chatbot 2025 API. Use POST /chat to talk to the bot."}
