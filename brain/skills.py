from datetime import datetime


def greeting_skill():
    return "Hello! I’m Vaani. How can I help you?"


def time_skill():
    now = datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def fallback_skill():
    return "Sorry, I didn’t understand that. Can you rephrase?"