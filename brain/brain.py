from brain.intents import detect_intent
from brain.memory import add_todo, list_todos, add_journal, add_reminder, get_due_reminders
from datetime import datetime


WAKE_WORDS = ["vaani", "vani", "wani"]


def strip_wake_word(text: str) -> str:
    for w in WAKE_WORDS:
        if text.startswith(w):
            return text[len(w):].strip()
    return text


def process_text(text: str) -> str:
    text = text.lower().strip()

    if not any(text.startswith(w) for w in WAKE_WORDS):
        return ""

    text = strip_wake_word(text)

    if not text:
        return "Yes?"

    intent, content = detect_intent(text)

    if intent == "add_todo":
        add_todo(content)
        return f"Task added: {content}"

    if intent == "list_todos":
        todos = list_todos()
        return "Your tasks are: " + ", ".join(todos) if todos else "No tasks."

    if intent == "journal":
        add_journal(content)
        return "Saved to journal."

    if intent == "reminder_relative":
        task, delta = content
        remind_time = datetime.now() + delta
        add_reminder(task, remind_time)
        return f"Reminder set for {task}"

    if intent == "time":
        return datetime.now().strftime("Time is %I:%M %p")

    if intent == "date":
        return datetime.now().strftime("Today is %B %d, %Y")

    if intent == "exit":
        return "__exit__"

    if intent == "greet":
        return "Hello! How can I help you?"

    return "Sorry, I didn’t understand."