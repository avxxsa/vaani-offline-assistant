from datetime import datetime
import re

def handle_time():
    return f"The current time is {datetime.now().strftime('%H:%M')}"

def handle_exit():
    return "__EXIT__"

def handle_unknown():
    return "I heard you, but I can't handle that request yet."

def handle_reminder(text: str):
    """
    Basic reminder parsing (Phase 1)
    """
    time_match = re.search(r'(\d{1,2})(?:\s*:\s*(\d{2}))?\s*(am|pm)?', text)

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridian = time_match.group(3)

        if meridian == "pm" and hour < 12:
            hour += 12

        time_str = f"{hour:02d}:{minute:02d}"
    else:
        time_str = "unspecified time"

    return f"Reminder noted for {time_str}. (Storage will be added next)"