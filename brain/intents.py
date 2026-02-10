import re

def detect_intent(text: str):
    t = text.lower().strip()
    print(f"DEBUG: detect_intent input: '{text}' -> normalized: '{t}'", flush=True)

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
    if t.startswith("add task") or t.startswith("काम थप") or t.startswith("task add"):
        content = t.replace("add task", "").replace("काम थप", "").replace("task add", "").strip()
        return "add_todo", content, None

    if any(p in t for p in ["list tasks", "show tasks", "काम देखाऊ", "लिस्ट देखाऊ"]):
        return "list_todos", None, None

    # JOURNAL
    if any(p in t for p in ["read notes", "show notes", "list notes", "show journal", "नोट देखाऊ", "नोट पढ"]):
        return "list_journal", None, None

    if t.startswith("note") or t.startswith("journal") or t.startswith("नोट"):
        content = t.replace("note", "").replace("journal", "").replace("नोट", "").strip()
        return "journal", content, None

    # GREET
    if any(w in t for w in ["hi", "hello", "namaste", "नमस्ते"]):
        return "greet", None, None

    return "unknown", None, None

    if "help" in t or "सहायता" in t:
        return "help", None, None
