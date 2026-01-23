from brain.brain import process_text

def main():
    print("Vaani (Text Mode)")
    print("Type something. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        response = process_text(user_input)

        if response == "__EXIT__":
            print("Vaani: Goodbye")
            break

        print("Vaani:", response)


if __name__ == "__main__":
    main()