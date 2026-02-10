<<<<<<< HEAD
<<<<<<< HEAD
from brain.intents import detect_intent
from brain.memory import add_todo, list_todos, add_journal, add_reminder, set_profile, get_profile
import time
from datetime import datetime, timedelta
import re

def parse_time_string(time_str: str):
    now = datetime.now()
    time_str = time_str.replace("pm", " pm").replace("am", " am")

    # 5 pm / 5 am
    m = re.search(r"(\d{1,2})\s*(am|pm)", time_str)
    if m:
        hour = int(m.group(1))
        if m.group(2) == "pm" and hour != 12:
            hour += 12
        return now.replace(hour=hour, minute=0, second=0).timestamp()

    # 5 baje
    m = re.search(r"(\d{1,2})\s*baje", time_str)
    if m:
        hour = int(m.group(1))
        return now.replace(hour=hour, minute=0, second=0).timestamp()

    # fallback: 1 minute later
    return time.time() + 60

def process_text(text: str) -> str:
    intent, content, time_info = detect_intent(text)
    data = None

    if intent == "add_todo":
        add_todo(content)
        return f"Task added: {content}"

    if intent == "list_todos":
        todos = list_todos()
        return "Your tasks are: " + ", ".join(todos) if todos else "Todo list is empty."

    if intent == "journal":
        add_journal(content)
        return "Saved to your journal."

    if intent == "set_reminder":
        task, time_str = data
        add_reminder(task, time_str)
        if is_nepali(text):
            return time_str + " बजे म तपाईंलाई " + task + " सम्झाउनेछु"
        return "Okay, I will remind you to " + task + " at " + time_str


    if intent == "get_time":
        now = datetime.now().strftime("%H:%M")
        if is_nepali(text):
            return "अहिले समय " + now + " बजे हो"
        return "Time is " + now

    if intent == "get_date":
        today = datetime.now().strftime("%Y-%m-%d")
        if is_nepali(text):
            return "आजको मिति " + today + " हो"
        return "Today's date is " + today

    if intent == "set_name":
        name = data
        if is_nepali(text):
            return "ठिक छ, म तपाईंलाई " + name + " भनेर बोलाउँछु"
        return "Okay, I will call you " + name

    if intent == "get_name":
        name = get_profile("name")
        return f"Your name is {name}" if name else "I don't know your name yet."

    if intent == "exit":
        return "__exit__"

    if intent == "greet":
        if is_nepali(text):
            return "नमस्ते! म तपाईंको सहायक हुँ।"
        return "Hello! I am your assistant."

    return "Sorry, I didn't understand that."

    if intent == "help":
        if is_nepali(text):
            return "तपाईं समय, मिति, रिमाइन्डर र नाम सोध्न सक्नुहुन्छ"
    return "You can ask time, date, reminders and your name."

def is_nepali(text):
    return any("अ" <= c <= "ह" for c in text)
=======
=======
>>>>>>> origin/pratistha/ui
from brain.memory import add_todo, get_todos, add_journal
from datetime import datetime

def process_text(text):
    text = text.lower()

    # EXIT
    if text in ["exit", "quit", "bye"]:
        return "__EXIT__"

    # TODO
    if "remind me to" in text or "add task" in text:
        task = text.replace("remind me to", "").replace("add task", "").strip()
        add_todo(task)
        return f"Got it. I saved your task: {task}"

    if "show my tasks" in text or "what are my tasks" in text:
        todos = get_todos()
        if not todos:
            return "You have no tasks."
        return "Your tasks:\n" + "\n".join(f"- {t}" for t in todos)

    # JOURNAL
    if "journal" in text or "today i" in text:
        entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {text}"
        add_journal(entry)
        return "Journal entry saved."

    # TIME
    if "time" in text:
        return datetime.now().strftime("Current time is %H:%M")

    # FALLBACK
<<<<<<< HEAD
    return "I understood you, but I don't know how to help with that yet."
>>>>>>> origin/suprabha/speech-layer
=======
    return "I understood you, but I don't know how to help with that yet."
>>>>>>> origin/pratistha/ui
