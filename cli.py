import numpy as np
import time

from audio_input import get_mic_stream
from vad_simple import frame_rms
from stt_nepali_hf_local import NepaliSTT
from tts_espeaking import speak_text
from brain.brain import process_text
from brain.memory import get_due_reminders
from brain.memory import check_reminders
from config import FRAMES_PER_BUFFER, END_SILENCE_SEC

print("Starting voice assistant...")

stream = get_mic_stream()
stt = NepaliSTT()

buffer = []
speaking = False
silence_start = None

while True:
    data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16)

    rms = frame_rms(audio)

    # CHECK REMINDERS
    due = get_due_reminders()
    for r in due:
        print("⏰ Reminder:", r["text"])
        speak_text("Reminder: " + r["text"])

    if rms > 500:  # speech threshold
        if not speaking:
            print("🎤 Listening...")
            speaking = True
            buffer = []
        buffer.append(audio)
        silence_start = None

    else:
        if speaking:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > END_SILENCE_SEC:
                print("🛑 Processing...")

                utterance = np.concatenate(buffer)
                text = stt.transcribe_int16(utterance)

                print("You said:", text)

                if text.strip():
                    text = text.lower().strip()

                    # WAKE WORD CHECK
                    if not text.startswith("vaani"):
                        print("Ignored (no wake word):", text)
                        speaking = False
                        buffer = []
                        continue

                    command = text.replace("vaani", "", 1).strip()

                    if not command:
                        speak_text("Yes?")
                        speaking = False
                        buffer = []
                        continue

                    reply = process_text(command)

                    if reply == "__exit__":
                        speak_text("Goodbye")
                        break

                    if reply:
                        print("Assistant:", reply)
                        speak_text(reply)

                speaking = False
                buffer = []