import numpy as np
import time
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def send_to_ui(type_, data):
    msg = {
        "type": type_,
        "data": data
    }
    print(json.dumps(msg))
    sys.stdout.flush()
    
send_to_ui("status", "python_started")



from audio_input import get_mic_stream
from vad_simple import frame_rms
from stt_nepali_hf_local import NepaliSTT
from tts_espeaking import speak_text
from brain.brain import process_text
from brain.memory import get_due_reminders
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

    due = get_due_reminders()
    for r in due:
        print("⏰ Reminder:", r["text"])
        speak_text("Reminder: " + r["text"])

    if rms > 500:  # speech threshold
        if not speaking:
            send_to_ui("status", "listening")

            speaking = True
            buffer = []
        buffer.append(audio)
        silence_start = None

    else:
        if speaking:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > END_SILENCE_SEC:
                send_to_ui("status", "processing")


                utterance = np.concatenate(buffer)
                text = stt.transcribe_int16(utterance)

                send_to_ui("user", text)


                if text.strip():
                    reply = process_text(text)

                    if reply == "__exit__":
                        speak_text("Goodbye")
                        break

                    if reply:
                        send_to_ui("assistant", reply)

                        speak_text(reply)

                speaking = False
                buffer = []

    