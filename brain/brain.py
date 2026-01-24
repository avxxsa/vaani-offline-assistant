from brain.intents import detect_intent
from brain.memory import add_todo, list_todos, add_journal
from brain.chat import get_chat_reply
from brain.emotion import detect_emotion

def process_text(text: str) -> str:
    intent, content = detect_intent(text)

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

    # EMOTION DETECTION
    emotion = detect_emotion(text)
    if emotion == "sad":
        return "I'm sorry you're feeling sad. Do you want to talk about it?"
    if emotion == "happy":
        return "That's great to hear! I'm glad you're feeling happy."
    if emotion == "angry":
        return "I can hear you're angry. Want to vent?"
    if emotion == "tired":
        return "You sound tired. Maybe you should rest a bit."
    if emotion == "stressed":
        return "That sounds stressful. Try taking a deep breath."

    # CHAT MODE
    chat_reply = get_chat_reply(text)
    if chat_reply:
        return chat_reply

    return "Sorry, I didn't understand that."