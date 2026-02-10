import json
import os
<<<<<<< HEAD
import time
from datetime import datetime

MEMORY_FILE = "brain/memory.json"

# ---------- CORE ----------
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"todos": [], "journal": [], "reminders": [], "profile": {}}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # backward compatibility
    data.setdefault("todos", [])
    data.setdefault("journal", [])
    data.setdefault("reminders", [])
    data.setdefault("profile", {})

    return data


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------- TIME PARSER ----------
def parse_time_string(t: str):
    """
    Converts '5 baje' or '5 pm' into unix timestamp (today)
    """
    try:
        t = t.replace("baje", "").replace("बजे", "").strip()

        now = datetime.now()
        hour = int("".join(c for c in t if c.isdigit()))

        if "pm" in t and hour < 12:
            hour += 12

        remind_time = now.replace(hour=hour, minute=0, second=0)

        if remind_time.timestamp() < time.time():
            remind_time = remind_time.replace(day=now.day + 1)

        return remind_time.timestamp()
    except:
        return time.time() + 60  # fallback 1 min later


# ---------- TODO ----------
def add_todo(task: str):
    data = load_memory()
    data["todos"].append(task)
    save_memory(data)


def list_todos():
    return load_memory()["todos"]


# ---------- JOURNAL ----------
def add_journal(entry: str):
    data = load_memory()
    data["journal"].append({
        "text": entry,
        "time": time.ctime()
    })
    save_memory(data)


# ---------- REMINDER ----------
def add_reminder(text: str, remind_time: str):
    data = load_memory()
    ts = parse_time_string(remind_time)

    data["reminders"].append({
        "text": text,
        "time": ts
    })
    save_memory(data)


def get_due_reminders():
    data = load_memory()
    now = time.time()

    due = [r for r in data["reminders"] if r["time"] <= now]
    data["reminders"] = [r for r in data["reminders"] if r["time"] > now]

    save_memory(data)
    return due


# ---------- PROFILE ----------
def set_profile(key, value):
    data = load_memory()
    data["profile"][key] = value
    save_memory(data)


def get_profile(key):
    return load_memory().get("profile", {}).get(key)

last_intent = None

def set_last_intent(i):
    global last_intent
    last_intent = i

def get_last_intent():
    return last_intent
=======

MEMORY_FILE = "brain/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"todos": [], "journal": []}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_todo(task):
    memory = load_memory()
    memory["todos"].append(task)
    save_memory(memory)

def get_todos():
    return load_memory()["todos"]

def add_journal(entry):
    memory = load_memory()
    memory["journal"].append(entry)
    save_memory(memory)

def get_journal():
    return load_memory()["journal"]
>>>>>>> origin/suprabha/speech-layer
