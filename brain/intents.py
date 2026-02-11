import re

def detect_intent(text: str):
    t = text.lower().strip()
    print(f"DEBUG: detect_intent input length: {len(text)}", flush=True)

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

    # TODO - List or Show
    if any(p in t for p in ["list tasks", "show tasks", "काम देखाऊ", "लिस्ट देखाऊ", "my tasks", "show my tasks"]):
        return "list_todos", None, None

    # TODO - Add
    if t.startswith("add task") or t.startswith("काम थप") or t.startswith("task add"):
        content = t.replace("add task", "").replace("काम थप", "").replace("task add", "").strip()
        return "add_todo", content, None

    # JOURNAL - List or Show
    if any(p in t for p in ["read notes", "show notes", "list notes", "show journal", "show journals", "नोट देखाऊ", "नोट पढ", "list journals", "my journals", "show my journals"]):
        return "list_journal", None, None

    # JOURNAL - Add entry (including "add journal", "journal add", etc.)
    if t.startswith("note") or t.startswith("journal") or t.startswith("नोट") or t.startswith("add journal") or t.startswith("add note"):
        # Extract content - handle various patterns: "journal gara", "journal add gara", "add journal gara", etc.
        content = re.sub(r"^(add\s+)?(journal|note|नोट)\s+", "", t).strip()
        content = re.sub(r"^(add\s+)?", "", content).strip()  # Remove any leftover "add " prefix
        return "journal", content, None

    # GREET
    if any(w in t for w in ["hi", "hello", "namaste", "नमस्ते"]):
        return "greet", None, None

    # HELP
    if "help" in t or "सहायता" in t:
        return "help", None, None

    return "unknown", None, None
