from brain.intents import detect_intent
from brain.memory import add_todo, list_todos, add_journal
from brain.chat import get_chat_reply

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

    # 🧠 NEW: CHAT MODE
    chat_reply = get_chat_reply(text)
    if chat_reply:
        return chat_reply

    return "Sorry, I didn't understand that."