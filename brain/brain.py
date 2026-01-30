from datetime import datetime
from brain.memory import set_profile, get_profile
from brain.intents import detect_intent
from brain.memory import add_todo, list_todos, add_journal, add_reminder

def process_text(text: str) -> str:
    intent, content, time_info = detect_intent(text)

    if intent == "time":
        now = datetime.now()
        return f"It is {now.strftime('%I:%M %p')} now."

    if intent == "date":
        today = datetime.now()
        return f"Today is {today.strftime('%B %d, %Y')}."

    if intent == "add_reminder":
        if not content or not time_info:
            return "What should I remind you about and when?"
        add_reminder(content, time_info)
        return f"Okay, I will remind you to {content} at {time_info}"

    if intent == "add_todo":
        if not content:
            return "What task should I add?"
        add_todo(content)
        return f"Task added: {content}"

    if intent == "list_todos":
        todos = list_todos()
        if not todos:
            return "Your todo list is empty."
        return "Your tasks are: " + ", ".join(todos)

    if intent == "journal":
        if not content:
            return "What should I note?"
        add_journal(content)
        return "Saved to your journal."

    if intent == "greet":
        return "Hello! How can I help you?"
    
    if intent == "set_name":
        set_profile("name", content)
        return f"Nice to meet you, {content}."

    if intent == "get_name":
        name = get_profile("name")
        if name:
                return f"Your name is {name}."
        return "I don't know your name yet."

    if intent == "set_fact":
        set_profile("fact", content)
        return f"Okay, I will remember that you are {content}."

    return "Sorry, I didn't understand that."