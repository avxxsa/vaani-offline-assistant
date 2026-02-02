from brain.memory import add_todo, get_todos, add_journal
from datetime import datetime

def process_text(text):
    text = text.lower()

    # EXIT
    if text in ["exit", "quit", "bye"]:
        return "__EXIT__"

    # TODO
    if "remind me to" in text or "add task" in text:
        task = text.replace("remind me to", "").replace("add task", "").strip()
        add_todo(task)
        return f"Got it. I saved your task: {task}"

    if "show my tasks" in text or "what are my tasks" in text:
        todos = get_todos()
        if not todos:
            return "You have no tasks."
        return "Your tasks:\n" + "\n".join(f"- {t}" for t in todos)

    # JOURNAL
    if "journal" in text or "today i" in text:
        entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {text}"
        add_journal(entry)
        return "Journal entry saved."

    # TIME
    if "time" in text:
        return datetime.now().strftime("Current time is %H:%M")

    # FALLBACK
    return "I understood you, but I don't know how to help with that yet."