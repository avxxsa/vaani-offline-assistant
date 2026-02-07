import os
import json

TODO_FILE = "todos.json"

def add_todo(task: str):
    todos = get_todos()
    todos.append(task)
    _save_json(TODO_FILE, todos)

def get_todos():
    if not os.path.exists(TODO_FILE):
        return []
    return _load_json(TODO_FILE)

def delete_todo(task: str):
    todos = get_todos()
    if task in todos:
        todos.remove(task)
        _save_json(TODO_FILE, todos)
        return True
    return False

def _save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def _load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
