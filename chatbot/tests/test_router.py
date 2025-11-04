# chatbot/tests/test_router.py
from chatbot.router import local_reply

def test_name_capture_and_greet():
    s = {"user_name": None}
    assert "Nice to meet you" in local_reply("my name is priya", s)
    assert s["user_name"] == "Priya"
