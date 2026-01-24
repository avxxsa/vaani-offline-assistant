import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join("brain", "memory.json")

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({"todos": [], "journal": [], "reminders": []}, f)


def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# TODOS
def add_todo(task):
    data = load_memory()
    data["todos"].append(task)
    save_memory(data)


def list_todos():
    return load_memory()["todos"]


# JOURNAL
def add_journal(entry):
    data = load_memory()
    data["journal"].append({
        "text": entry,
        "time": datetime.now().isoformat()
    })
    save_memory(data)


# REMINDERS
def add_reminder(text, remind_time):
    data = load_memory()
    data["reminders"].append({
        "text": text,
        "time": remind_time.isoformat(),
        "done": False
    })
    save_memory(data)


def get_due_reminders():
    data = load_memory()
    now = datetime.now()
    due = []

    for r in data["reminders"]:
        if not r["done"]:
            t = datetime.fromisoformat(r["time"])
            if t <= now:
                due.append(r)
                r["done"] = True

    save_memory(data)
    return due