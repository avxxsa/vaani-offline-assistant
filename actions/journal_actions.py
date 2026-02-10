# actions/journal_actions.py
import os
import json
from datetime import datetime

JOURNAL_FILE = "journal.json"

def add_journal(entry: str):
    journals = get_journals()
    timestamped_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {entry}"
    journals.append(timestamped_entry)
    _save_json(JOURNAL_FILE, journals)

def get_journals():
    if not os.path.exists(JOURNAL_FILE):
        return []
    return _load_json(JOURNAL_FILE)

def delete_journal_by_index(index: int):
    journals = get_journals()
    if 0 <= index < len(journals):
        removed = journals.pop(index)
        _save_json(JOURNAL_FILE, journals)
        return True, removed
    return False, None

# --- Helper functions ---
def _save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def _load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
