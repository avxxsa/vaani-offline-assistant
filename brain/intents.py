import re

def detect_intent(text: str):
    text = text.lower().strip()

    # NAME SET
    m = re.search(r"my name is (.+)", text)
    if m:
        return "set_name", m.group(1), None

    # ASK NAME
    if "what is my name" in text:
        return "get_name", "", None

    # FACT
    m = re.search(r"i am (.+)", text)
    if m:
        return "set_fact", m.group(1), None

    # TIME
    if any(p in text for p in ["time", "kati baje", "ahile kati baje"]):
        return "time", "", None

    # DATE
    if any(p in text for p in ["date", "today", "aaja ko date"]):
        return "date", "", None

    # ADD TODO
    if text.startswith("add task"):
        task = text.replace("add task", "").strip()
        return "add_todo", task, None

    # LIST TODO
    if "list tasks" in text or "show tasks" in text:
        return "list_todos", "", None

    # JOURNAL
    if text.startswith("note"):
        note = text.replace("note", "").strip()
        return "journal", note, None

    # REMINDER (example)
    match = re.search(r"remind me to (.+) at (.+)", text)
    if match:
        task = match.group(1)
        time_info = match.group(2)
        return "reminder", task, time_info

    # GREET
    if any(w in text for w in ["hello", "hi", "namaste"]):
        return "greet", "", None

    return "unknown", text, None
