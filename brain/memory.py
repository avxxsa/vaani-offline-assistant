import json
import os
import time

MEMORY_FILE = "brain/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"todos": [], "journal": [], "reminders": []}

    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    # backward compatibility (old memory.json)
    if "todos" not in data:
        data["todos"] = []
    if "journal" not in data:
        data["journal"] = []
    if "reminders" not in data:
        data["reminders"] = []

    return data

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# TODO
def add_todo(task: str):
    data = load_memory()
    data["todos"].append(task)
    save_memory(data)

def list_todos():
    return load_memory()["todos"]


# JOURNAL
def add_journal(entry: str):
    data = load_memory()
    data["journal"].append({
        "text": entry,
        "time": time.ctime()
    })
    save_memory(data)


# REMINDERS
def add_reminder(text: str, remind_time: float):
    data = load_memory()
    data["reminders"].append({
        "text": text,
        "time": remind_time
    })
    save_memory(data)

def get_due_reminders():
    data = load_memory()
    now = time.time()

    due = [r for r in data["reminders"] if r["time"] <= now]
    data["reminders"] = [r for r in data["reminders"] if r["time"] > now]

    save_memory(data)
    return due