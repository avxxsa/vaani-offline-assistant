from skills.reminder import set_reminder
from skills.general import greeting

def route_intent(intent, entities):

    if intent == "SET_REMINDER":
        return set_reminder(entities)

    if intent == "GREETING":
        return greeting()

    if intent == "EXIT":
        return {"exit": True}

    return {"error": "unknown_intent"}