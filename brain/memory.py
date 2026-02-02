import json
import os

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