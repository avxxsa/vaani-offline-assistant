def detect_intent(text: str) -> str:
    text = text.lower().strip()

    if any(word in text for word in ["remind", "reminder"]):
        return "REMINDER"

    if any(word in text for word in ["time", "clock"]):
        return "TIME"

    if any(word in text for word in ["exit", "quit", "bye"]):
        return "EXIT"

    return "UNKNOWN"