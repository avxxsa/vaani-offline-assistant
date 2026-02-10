import re

def detect_intent(text: str):
    t = text.lower().strip()

    # NAME
    m = re.search(r"my name is (.+)", t)
    if m:
        return "set_name", m.group(1), None

    if "what is my name" in t:
        return "get_name", None, None

    # EXIT
    if t in ["exit", "quit", "bye", "stop"]:
        return "exit", None, None

    # TIME
    if any(p in t for p in ["what time", "time is it", "kati baje", "कति बजे"]):
        return "get_time", None, None

    # DATE
    if any(p in t for p in ["today date", "aaja ko date", "आजको मिति"]):
        return "get_date", None, None

    # REMINDER
    m = re.search(r"remind me to (.+) at (.+)", t)
    if m:
        return "add_reminder", m.group(1), m.group(2)

    m = re.search(r"malai (.+) samjhau (.+)", t)
    if m:
        return "add_reminder", m.group(1), m.group(2)

    # TODO
    if t.startswith("add task"):
        return "add_todo", t.replace("add task", "").strip(), None

    if "list tasks" in t:
        return "list_todos", None, None

    # JOURNAL
    if t.startswith("note"):
        return "journal", t.replace("note", "").strip(), None

    # GREET
    if any(w in t for w in ["hi", "hello", "namaste", "नमस्ते"]):
        return "greet", None, None

    return "unknown", None, None

    if "help" in t or "सहायता" in t:
        return "help", None, None
