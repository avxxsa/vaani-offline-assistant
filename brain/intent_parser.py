import re

def detect_intent(text: str) -> str:
    text = text.lower().strip()

    if text in ["hi", "hello", "hey"]:
        return "greet"

    if "time" in text:
        return "time"

    if text in ["exit", "quit", "bye"]:
        return "exit"

    if "remind" in text:
        return "reminder"

    if "todo" in text:
        return "todo"

    if "journal" in text:
        return "journal"

    return "unknown"