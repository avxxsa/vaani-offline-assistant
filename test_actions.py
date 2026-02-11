# test_actions_safe.py
import os
import json
from actions.general_actions import greeting, time_skill, fallback_skill
from actions.todo_actions import add_todo, get_todos, delete_todo
from actions.reminder_actions import set_reminder, get_reminders, delete_reminder
from actions.journal_actions import add_journal, get_journals, delete_journal_by_index
from actions.system_actions import get_platform, get_system_info
from actions.search_actions import local_file_search, search_in_common_locations, web_search

# --- Helpers to prevent overwriting real files ---
def safe_add_todo(task):
    todos_backup = get_todos().copy()
    add_todo(task)
    todos_after = get_todos()
    _restore_todos(todos_backup)
    return todos_after

def _restore_todos(todos_list):
    with open("todos.json", "w") as f:
        json.dump(todos_list, f, indent=2)

def safe_add_journal(entry):
    journals_backup = get_journals().copy()
    add_journal(entry)
    journals_after = get_journals()
    _restore_journals(journals_backup)
    return journals_after

def _restore_journals(journals_list):
    with open("journal.json", "w") as f:
        json.dump(journals_list, f, indent=2)

def safe_set_reminder(entities):
    reminders_backup = get_reminders().copy()
    result = set_reminder(entities)
    reminders_after = get_reminders()
    _restore_reminders(reminders_backup)
    return result, reminders_after

def _restore_reminders(reminders_list):
    with open("reminders.json", "w") as f:
        json.dump(reminders_list, f, indent=2)

# --- Testing starts ---
print("=== General Actions ===")
print(greeting())
print(time_skill())
print(fallback_skill())

print("\n=== TODO Actions ===")
todos_result = safe_add_todo("Test task")
print("Todos after adding 'Test task':", todos_result)

print("\n=== Reminder Actions ===")
reminder_result, reminders_after = safe_set_reminder({"task": "Call mom", "time": "23:59"})
print("Set reminder result:", reminder_result)
print("Reminders after safe test:", reminders_after)

print("\n=== Journal Actions ===")
journals_result = safe_add_journal("This is a safe test entry")
print("Journals after safe test entry:", journals_result)

print("\n=== System Actions ===")
print("Platform:", get_platform())
print("System info:", get_system_info())

print("\n=== Search Actions ===")
local_results = local_file_search("test")
print("Local file search results (max 10):", local_results)

common_results = search_in_common_locations("test")
print("Search in common locations (max 10):", common_results)

# For web_search, print the URL instead of opening browser
query = "Python programming"
search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
print("Web search would open:", search_url)
