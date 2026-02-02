def route_intent(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["hi", "hello", "hey"]):
        return "greeting"

    if "time" in text:
        return "time"

    return "fallback"