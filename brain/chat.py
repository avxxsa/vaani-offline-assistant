import random

CHAT_RESPONSES = {
    "how are you": [
        "I'm doing well, thanks for asking!",
        "All good. How about you?",
        "Feeling helpful as always."
    ],
    "what is your name": [
        "My name is Vaani.",
        "You can call me Vaani.",
        "I am your voice assistant."
    ],
    "who made you": [
        "I was created by my developers.",
        "I was built as a college project.",
        "I was made with Python."
    ],
    "thank you": [
        "You're welcome!",
        "Happy to help.",
        "Anytime!"
    ],
    "goodbye": [
        "Goodbye!",
        "See you later.",
        "Take care!"
    ]
}

def get_chat_reply(text: str) -> str | None:
    text = text.lower().strip()

    for key in CHAT_RESPONSES:
        if key in text:
            return random.choice(CHAT_RESPONSES[key])

    return None