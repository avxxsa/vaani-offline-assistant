# Vaani — Offline AI Personal Assistant

Vaani is a fully offline, privacy-first AI voice assistant designed to run on-device without any internet connection. It uses local speech recognition (Vosk), text-to-speech (pyttsx3), and a modular Python architecture to interpret commands and perform tasks such as opening applications, checking time/date, setting reminders, and more.

---

## Tech Stack

- **Python**
- **Vosk** – Offline speech recognition  
- **pyttsx3** – Text-to-speech  
- **Regex & Rule-based NLP** – Intent parsing  
- **SQLite / JSON** (local data storage)  
- **Optional:** PyQt for GUI

---

## Setup Instructions

1. Create a virtual environment:
   ```bash 
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate

2. Install Dependencies:
    `pip install -r requirements.txt`