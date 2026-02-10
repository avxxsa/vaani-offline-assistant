# actions/reminder_actions.py
import os
import json
from datetime import datetime, timedelta

REMINDER_FILE = "reminders.json"

def set_reminder(entities: dict):
    """
    entities example: {"task": "call mom", "time": "15:30"}
    """
    task = entities.get("task")
    time_str = entities.get("time")

    if not task or not time_str:
        return {"success": False}

    try:
        reminder_time = datetime.strptime(time_str, "%H:%M")
        now = datetime.now()
        reminder_datetime = datetime.combine(now.date(), reminder_time.time())
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)

        reminders = _load_reminders()
        reminders.append({"task": task, "time": reminder_datetime.strftime("%Y-%m-%d %H:%M")})
        _save_reminders(reminders)

        return {"success": True, "time": reminder_datetime.strftime("%I:%M %p")}
    except Exception as e:
        return {"success": False}

def get_reminders():
    return _load_reminders()

def delete_reminder(index: int):
    reminders = _load_reminders()
    if 0 <= index < len(reminders):
        removed = reminders.pop(index)
        _save_reminders(reminders)
        return True, removed
    return False, None

# --- Helper functions ---
def _load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, "r") as f:
        return json.load(f)

def _save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=2)
