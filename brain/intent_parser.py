import re

def parse_intent(text: str):
    text = text.lower()

    # EXIT
    if text in ["exit", "quit", "stop", "bye bye"]:
        return "EXIT", {}

    # REMINDER
    if "remind" in text:
        task_match = re.search(r"remind me to (.+?) at", text)
        time_match = re.search(r"at (.+)", text)

        task = task_match.group(1) if task_match else None
        time = time_match.group(1) if time_match else None

        return "SET_REMINDER", {
            "task": task,
            "time": time
        }

    # GREETING
    if text in ["hi", "hello", "hey"]:
        return "GREETING", {}

    return "UNKNOWN", {}