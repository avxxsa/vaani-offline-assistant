print("brain.py loaded")

def process_input(text: str) -> str:
    """
    Core brain logic.
    This will later expand into intents, memory, reminders, etc.
    """
    text = text.lower().strip()

    if text in ["hi", "hello", "hey"]:
        return "Hello! How can I help you?"

    elif "time" in text:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%H:%M')}"

    elif text in ["exit", "quit", "bye"]:
        return "__EXIT__"

    else:
        return "I understood your input, but this feature is not implemented yet."


def main():
    print("Vaani Brain is running (text-only mode)")
    print("Type 'exit' to stop\n")

    while True:
        user_input = input("User: ")
        response = process_input(user_input)

        if response == "__EXIT__":
            print("Vaani: Goodbye!")
            break

        print("Vaani:", response)


if __name__ == "__main__":
    main()