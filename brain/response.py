def generate_response(intent, result):

    if intent == "SET_REMINDER":
        if result.get("success"):
            return f"Reminder set for {result['time']}."
        else:
            return "I could not set the reminder."

    if intent == "GREETING":
        return result.get("message")

    if intent == "EXIT":
        return "ByeBye. Take care. See you."

    if intent == "UNKNOWN":
        return "Sorry, I didn't understand that."

    return "Done."