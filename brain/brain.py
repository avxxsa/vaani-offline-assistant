from brain.intent_parser import detect_intent
from brain.handlers import (
    handle_greet,
    handle_time,
    handle_exit,
    handle_reminder,
    handle_todo,
    handle_journal,
    handle_unknown
)

print("brain.py loaded")

def process_text(text: str) -> str:
    intent = detect_intent(text)

    if intent == "greet":
        return handle_greet()

    elif intent == "time":
        return handle_time()

    elif intent == "exit":
        return handle_exit()

    elif intent == "reminder":
        return handle_reminder(text)

    elif intent == "todo":
        return handle_todo(text)

    elif intent == "journal":
        return handle_journal(text)

    else:
        return handle_unknown()