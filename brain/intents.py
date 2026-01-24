import re
from datetime import datetime, timedelta


def detect_intent(text: str):
    text = text.lower().strip()

    # REMINDER: "remind me to study in 10 minutes"
    match = re.search(r"remind me (.*) in (\d+) (minute|minutes|hour|hours)", text)
    if match:
        task = match.group(1)
        num = int(match.group(2))
        unit = match.group(3)

        delta = timedelta(minutes=num) if "minute" in unit else timedelta(hours=num)
        return "reminder_relative", (task, delta)

    if text.startswith("add task"):
        return "add_todo", text.replace("add task", "").strip()

    if text.startswith("note"):
        return "journal", text.replace("note", "").strip()

    if "list tasks" in text:
        return "list_todos", ""

    if "time" in text:
        return "time", ""

    if "date" in text:
        return "date", ""

    if "exit" in text:
        return "exit", ""

    if text in ["hi", "hello"]:
        return "greet", ""

    return "unknown", text