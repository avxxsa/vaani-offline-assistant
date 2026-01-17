import json
from pathlib import Path

DB = Path("brain/data/reminders.json")

def set_reminder(entities):
    task = entities.get("task")
    time = entities.get("time")

    if not task or not time:
        return {"success": False}

    DB.parent.mkdir(exist_ok=True)

    if DB.exists():
        data = json.loads(DB.read_text())
    else:
        data = []

    data.append({
        "task": task,
        "time": time
    })

    DB.write_text(json.dumps(data, indent=2))

    return {
        "success": True,
        "task": task,
        "time": time
    }