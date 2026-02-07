import re
import time
from datetime import datetime, timedelta

def parse_reminder(text: str):
    text = text.lower()

    match = re.search(r"remind me to (.+) at (\d{1,2})(:(\d{2}))?\s*(am|pm)?", text)
    if not match:
        return None, None

    task = match.group(1)
    hour = int(match.group(2))
    minute = int(match.group(4)) if match.group(4) else 0
    ampm = match.group(5)

    if ampm:
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0

    now = datetime.now()
    remind_time = now.replace(hour=hour, minute=minute, second=0)

    if remind_time < now:
        remind_time += timedelta(days=1)

    return task, remind_time.timestamp()