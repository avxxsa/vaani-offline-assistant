from brain.intents import detect_intent
from brain.memory import add_todo, list_todos, add_journal, add_reminder, set_profile, get_profile, get_journal
from brain.llm_response import generate_response as generate_llm_response, is_ollama_available
import time
from datetime import datetime, timedelta
import re

def parse_time_string(time_str: str):
    now = datetime.now()
    time_str = time_str.replace("pm", " pm").replace("am", " am")

    # 5 pm / 5 am
    m = re.search(r"(\d{1,2})\s*(am|pm)", time_str)
    if m:
        hour = int(m.group(1))
        if m.group(2) == "pm" and hour != 12:
            hour += 12
        return now.replace(hour=hour, minute=0, second=0).timestamp()

    # 5 baje
    m = re.search(r"(\d{1,2})\s*baje", time_str)
    if m:
        hour = int(m.group(1))
        return now.replace(hour=hour, minute=0, second=0).timestamp()

    # fallback: 1 minute later
    return time.time() + 60

def is_nepali(text):
    return any("अ" <= c <= "ह" for c in text)

def process_text(text: str) -> str:
    # Lowercase text for simple matches (from suprabha)
    text_lower = text.lower()

    # Simple exit commands
    if text_lower in ["exit", "quit", "bye"]:
        return "__EXIT__"

    intent, content, time_info = detect_intent(text)
    data = None
    print(f"DEBUG: process_text detected intent='{intent}' ({len(text)} chars input)", flush=True)

    # ADD TODO
    if intent == "add_todo":
        add_todo(content)
        return f"Task added: {content}"

    # LIST TODOS
    if intent == "list_todos":
        todos = list_todos()
        return "Your tasks are: " + ", ".join(todos) if todos else "Todo list is empty."

    # LIST JOURNALS
    if intent == "list_journal":
        journals = get_journal()
        if journals:
            # Format journals for speech (last 5 entries)
            entries = "\n".join([f"- {j['text']}" for j in journals[-5:]])
            return f"Here are your recent journal entries:\n{entries}"
        return "You don't have any journal entries yet."

    # ADD JOURNAL
    if intent == "journal":
        add_journal(content)
        return "Saved to your journal."

    # REMINDER
    if intent == "set_reminder":
        if data is None and time_info is not None:
            task = content
            add_reminder(task, time_info)
            return f"Okay, I will remind you to {task} at {time_info}"
        elif data is not None:
            task, time_str = data
            add_reminder(task, time_str)
            return f"Okay, I will remind you to {task} at {time_str}"

    # TIME
    if intent == "get_time":
        now_str = datetime.now().strftime("%H:%M")
        return f"अहिले समय {now_str} बजे हो"

    # DATE
    if intent == "get_date":
        today = datetime.now().strftime("%Y-%m-%d")
        return f"आजको मिति {today} हो"

    # SET NAME
    if intent == "set_name":
        name = content  # Use content, not data (which is None)
        if name:
            set_profile("name", name)
            return f"ठिक छ, म तपाईंलाई {name} भनेर बोलाउँछु"
        return "मेरो नाम सुनिन सकेन। कृपया आफ्नो नाम भन्नुहोस्।"

    # GET NAME
    if intent == "get_name":
        name = get_profile("name")
        return f"मेरो नाम {name} हो" if name else "मलाई अझै तपाईंको नाम थाहा छैन।"

    # GREET
    if intent == "greet":
        response = "नमस्ते! म तपाईंको सहायक हुँ। म तपाईंलाई कसरी सहायता गर्न सक्छु?"
        print(f"DEBUG: Greet intent matched, response length={len(response)}", flush=True)
        return response

    # HELP
    if intent == "help":
        return "तपाईं समय, मिति, रिमाइन्डर, काम, नोट र आफ्नो नाम सोध्न सक्नुहुन्छ"

    # FALLBACK: Try LLM for intelligent response only if not a known action
    if intent == "unknown":
        print(f"DEBUG: Using LLM fallback for unknown intent, language=Nepali", flush=True)
        llm_response = generate_llm_response(text, is_nepali=True)
        
        if llm_response:
            print(f"DEBUG: Using LLM response", flush=True)
            return llm_response
    
    # Fallback for unhandled text when LLM unavailable
    if "remind me to" in text_lower or "add task" in text_lower:
        task = text_lower.replace("remind me to", "").replace("add task", "").strip()
        add_todo(task)
        return f"कार्य सुरक्षित गरियो: {task}"

    if "show my tasks" in text_lower or "what are my tasks" in text_lower:
        todos = list_todos()
        if not todos:
            return "तपाईंसँग कुनै कार्य छैन।"
        return "तपाईंको कार्य:\n" + "\n".join(f"- {t}" for t in todos)

    if "journal" in text_lower or "note" in text_lower:
        entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {text}"
        add_journal(entry)
        return "नोट सुरक्षित गरियो।"

    if "time" in text_lower:
        return datetime.now().strftime("अहिले समय %H:%M बजे हो")

    # Default fallback when LLM and rules fail
    return "मलाई समझ परेन। कृपया फेरि प्रयास गर्नुहोस्।"
