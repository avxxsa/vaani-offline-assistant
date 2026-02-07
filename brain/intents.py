import re

def detect_intent(text: str):
    t = text.lower().strip()

    # ---------- REMINDER (English) ----------
    m = re.search(r"remind me to (.+) at (.+)", t)
    if m:
        return "add_reminder", m.group(1), m.group(2)

    # ---------- REMINDER (Nepali romanized) ----------
    m = re.search(r"malai (.+) samjhau (.+)", t)
    if m:
        return "add_reminder", m.group(1), m.group(2)

    # ---------- TODO ----------
    if t.startswith("add task"):
        return "add_todo", t.replace("add task", "").strip(), None

    if "kam add" in t:
        return "add_todo", t.replace("kam add", "").strip(), None

    # ---------- LIST TODOS ----------
    if "list tasks" in t or "show tasks" in t or "mero task" in t:
        return "list_todos", None, None

    # ---------- JOURNAL ----------
    if t.startswith("note"):
        return "journal", t.replace("note", "").strip(), None

    if t.startswith("lekha"):
        return "journal", t.replace("lekha", "").strip(), None

    # ---------- GREETING ----------
    if t in ["hello", "hi", "hey", "namaste"]:
        return "greet", None, None

    return "unknown", None, None