import time
import re
from datetime import datetime

from brain.intents import detect_intent
from brain.memory import (
    add_todo,
    list_todos,
    add_journal,
    add_reminder,
    set_profile,
    get_profile,
)


def is_nepali(text: str) -> bool:
    return any("अ" <= c <= "ह" for c in text)


def parse_time_string(time_str: str) -> float:
    now = datetime.now()
    s = time_str.lower().strip().replace("pm", " pm").replace("am", " am")

    # 5 pm / 5 am
    m = re.search(r"(\d{1,2})\s*(am|pm)", s)
    if m:
        hour = int(m.group(1))
        mer = m.group(2)
        if mer == "pm" and hour != 12:
            hour += 12
        if mer == "am" and hour == 12:
            hour = 0
        return now.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp()

    # 5 baje
    m = re.search(r"(\d{1,2})\s*baje", s)
    if m:
        hour = int(m.group(1))
        return now.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp()

    # fallback: 1 minute later
    return time.time() + 60


def process_text(text: str) -> str:
    intent, content, time_info = detect_intent(text)

    # TODOs
    if intent == "add_todo":
        add_todo(content)
        return f"Task added: {content}"

    if intent == "list_todos":
        todos = list_todos()
        return "Your tasks are: " + ", ".join(todos) if todos else "Todo list is empty."

    # Journal
    if intent == "journal":
        add_journal(content)
        return "Saved to your journal."

    # Reminders
    if intent == "set_reminder":
        # Expect detect_intent to provide (task, time_str) in either content or time_info
        # Common patterns: content=(task, time_str) OR content=task, time_info=time_str
        task = None
        time_str = None

        if isinstance(content, (tuple, list)) and len(content) >= 2:
            task, time_str = content[0], content[1]
        else:
            task = content
            time_str = time_info

        if not task or not time_str:
            return "Please tell me what to remind you about and when."

        add_reminder(task, time_str)

        if is_nepali(text):
            return f"{time_str} बजे म तपाईंलाई {task} सम्झाउनेछु"
        return f"Okay, I will remind you to {task} at {time_str}"

    # Time / Date
    if intent == "get_time":
        now = datetime.now().strftime("%H:%M")
        if is_nepali(text):
            return f"अहिले समय {now} बजे हो"
        return f"Time is {now}"

    if intent == "get_date":
        today = datetime.now().strftime("%Y-%m-%d")
        if is_nepali(text):
            return f"आजको मिति {today} हो"
        return f"Today's date is {today}"

    # Profile name
    if intent == "set_name":
        name = content
        if not name:
            return "What name should I call you?"
        set_profile("name", name)
        if is_nepali(text):
            return f"ठिक छ, म तपाईंलाई {name} भनेर बोलाउँछु"
        return f"Okay, I will call you {name}"

    if intent == "get_name":
        name = get_profile("name")
        return f"Your name is {name}" if name else "I don't know your name yet."

    # Help / Exit / Greeting
    if intent == "help":
        if is_nepali(text):
            return "तपाईं समय, मिति, रिमाइन्डर, टुडु र नाम सोध्न सक्नुहुन्छ।"
        return "You can ask about time, date, reminders, todos, and your name."

    if intent == "exit":
        return "__exit__"

    if intent == "greet":
        if is_nepali(text):
            return "नमस्ते! म तपाईंको सहायक हुँ।"
        return "Hello! I am your assistant."

    return "Sorry, I didn't understand that."