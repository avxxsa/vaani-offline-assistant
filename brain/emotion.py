def detect_emotion(text: str) -> str | None:
    text = text.lower()

    if any(word in text for word in ["sad", "depressed", "upset", "unhappy", "cry"]):
        return "sad"

    if any(word in text for word in ["happy", "excited", "great", "good", "awesome"]):
        return "happy"

    if any(word in text for word in ["angry", "mad", "annoyed", "irritated"]):
        return "angry"

    if any(word in text for word in ["tired", "exhausted", "sleepy"]):
        return "tired"

    if any(word in text for word in ["stressed", "pressure", "anxious", "worried"]):
        return "stressed"

    return None