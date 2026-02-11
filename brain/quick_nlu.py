# quick_nlu.py
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Training examples-
training_sentences = [
    # Name
    "my name is Avipsa",
    "what is my name",

    # Exit
    "exit", "quit", "bye", "stop",

    # Time
    "what time is it", "time is it", "kati baje", "कति बजे",

    # Date
    "today date", "aaja ko date", "आजको मिति",

    # Reminders
    "remind me to submit report at 5",
    "malai report samjhau 5 baje",
    "note submit report",
    "add reminder",
    "list reminders", "show reminders", "reminders dekhau",
    "स्मरणपत्र देखाउ", "कार्यसूची देखाउ",

    # Todo
    "add task buy milk", "काम थप दूध किन",
    "task add homework",
    "list tasks", "show tasks", "काम देखाऊ", "लिस्ट देखाऊ",

    # Journal
    "read notes", "show notes", "list notes",
    "show journal", "नोट देखाऊ", "नोट पढ",
    "note meeting summary", "journal meeting summary",

    # Greet
    "hi", "hello", "namaste", "नमस्ते",

    # Help
    "help", "सहायता"
]

training_labels = [
    # Name
    "set_name", "get_name",

    # Exit
    "exit", "exit", "exit", "exit",

    # Time
    "get_time", "get_time", "get_time", "get_time",

    # Date
    "get_date", "get_date", "get_date",

    # Reminders
    "add_reminder", "add_reminder", "add_reminder", "add_reminder",
    "list_reminders", "list_reminders", "list_reminders",
    "list_reminders", "list_reminders",

    # Todo
    "add_todo", "add_todo", "add_todo",
    "list_todos", "list_todos", "list_todos", "list_todos",

    # Journal
    "list_journal", "list_journal", "list_journal",
    "list_journal", "list_journal", "list_journal",
    "journal", "journal",

    # Greet
    "greet", "greet", "greet", "greet",

    # Help
    "help", "help"
]

# Train classifier
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(training_sentences)
clf = MultinomialNB()
clf.fit(X, training_labels)

# Intent + slot detection
def detect_intent(text: str):
    t = text.lower().strip()
    print(f"DEBUG: detect_intent input length: {len(text)}", flush=True)

    # First try classifier
    try:
        X_test = vectorizer.transform([t])
        intent = clf.predict(X_test)[0]
    except Exception:
        intent = "unknown"

    # Slot extraction for reminders
    if intent == "add_reminder":
        m = re.search(r"remind me to (.+) at (.+)", t)
        if m:
            return "add_reminder", m.group(1), m.group(2)
        m = re.search(r"malai (.+) samjhau (.+)", t)
        if m:
            return "add_reminder", m.group(1), m.group(2)
        # fallback: just return text
        return "add_reminder", t, None

    # Slot extraction for todos
    if intent == "add_todo":
        content = t.replace("add task", "").replace("काम थप", "").replace("task add", "").strip()
        return "add_todo", content, None

    # Slot extraction for journal
    if intent == "journal":
        content = t.replace("note", "").replace("journal", "").replace("नोट", "").strip()
        return "journal", content, None

    # Other intents don’t need slots
    return intent, None, None

# Quick test
if __name__ == "__main__":
    tests = [
        "remind me to buy milk at 7",
        "list reminders",
        "काम थप पढाई",
        "note meeting summary",
        "hello",
        "आजको मिति",
        "what is my name",
        "help"
    ]
    for t in tests:
        print(f"Test (length {len(t)}) -> {detect_intent(t)}")
