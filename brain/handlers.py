from datetime import datetime

def handle_greet():
    return "Hello! How can I help you?"

def handle_time():
    return f"The current time is {datetime.now().strftime('%H:%M')}"

def handle_exit():
    return "__EXIT__"

def handle_reminder(text):
    return "Reminder noted. (Feature coming soon)"

def handle_todo(text):
    return "To-do noted. (Feature coming soon)"

def handle_journal(text):
    return "Journal entry saved. (Placeholder)"

def handle_unknown():
    return "I heard you, but I don't know how to handle that yet."