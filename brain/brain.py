print("brain.py loaded")

from handlers import greet, time_now, exit_reply, unknown

def process_input(text: str) -> dict:
    t = (text or "").lower().strip()

    if t in ["hi", "hello", "नमस्ते"]:
        return {"reply": greet(), "action": None}

    if "time" in t or "समय" in t:
        return {"reply": time_now(), "action": None}

    if t in ["exit", "quit", "bye", "बन्द", "रोक"]:
        return {"reply": exit_reply(), "action": "exit"}

    return {"reply": unknown(), "action": None}


def main():
    print("Vaani Brain is running (text-only mode)")
    print("Type 'exit' to stop\n")

    while True:
        user_input = input("User: ")
        result = process_input(user_input)

        print("Vaani:", result["reply"])

        if result["action"] == "exit":
            break


if __name__ == "__main__":
    main()