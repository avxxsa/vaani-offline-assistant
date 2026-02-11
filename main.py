# main.py - merged and safe version
import os
import json
import sys
import numpy as np
import threading

# Delay Kivy import to cli mode only
# from kivy.app import App
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.textinput import TextInput
# from kivy.uix.button import Button
# from kivy.uix.label import Label

from config import (
    SAMPLE_RATE, FRAMES_PER_BUFFER,
    NOISE_PROFILE_SEC, SPEECH_THRESHOLD_MULTIPLIER,
    END_SILENCE_SEC, MAX_UTTERANCE_SEC,
    HF_NEPALI_MODEL_PATH, ENABLE_NOISE_REDUCTION,
    NOISE_REDUCTION_STRENGTH, MIN_SPEECH_DURATION_SEC
)
from audio_input import get_mic_stream
from vad_simple import (
    frame_rms, is_speech,
    spectral_subtraction_simple,
    apply_high_pass_filter
)
from stt_nepali_hf_local import NepaliSTT
from tts_espeaking import NepaliTTS

# ---------- REPLY FUNCTION ----------
def generate_reply(user_text: str) -> str:
    """Generate a reply based on user input"""
    t = (user_text or "").strip()
    t_lower = t.lower()

    # Exit keywords (Nepali and English)
    if ("बन्द" in t or "रोक" in t or
            "bye" in t_lower or "बाय" in t or "exit" in t_lower or "quit" in t_lower or "stop" in t_lower):
        return "ठिक छ। फेरि भेटौँला।"

    if "नमस्ते" in t or "हेलो" in t:
        return "नमस्ते।"

    if "धन्यवाद" in t:
        return "स्वागत छ।"

    if "तिम्रो नाम के हो" in t or "के हो तिम्रो नाम" in t:
        return "मेरो नाम वाणी हो।"

    return f"तपाईंले भन्नुभयो: {t}"


# ---------- AUDIO & VAD HELPERS ----------
def calibrate_threshold(stream) -> tuple[float, np.ndarray]:
    noise_frames = []
    num_frames = int((NOISE_PROFILE_SEC * SAMPLE_RATE) / FRAMES_PER_BUFFER)

    print(f"Calibrating... Please stay quiet for {NOISE_PROFILE_SEC}s")
    for i in range(num_frames):
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        frame = np.frombuffer(data, dtype=np.int16)
        noise_frames.append(frame)
        if (i + 1) % 5 == 0:
            print(".", end="", flush=True)

    print()
    noise_sample = np.concatenate(noise_frames)
    threshold = frame_rms(noise_sample) * SPEECH_THRESHOLD_MULTIPLIER

    print(f"Noise profile captured")
    print(f"Threshold set to: {threshold:.1f}")
    print(f"Background noise level: {frame_rms(noise_sample):.1f}")

    return threshold, noise_sample


def record_utterance(stream, threshold: float, noise_profile: np.ndarray) -> np.ndarray:
    max_silent_frames = int(END_SILENCE_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
    max_total_frames = int(MAX_UTTERANCE_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
    min_speech_frames = int(MIN_SPEECH_DURATION_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)

    print("Listening...", end="", flush=True)
    speech_start_frames = 0

    while True:
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        frame = np.frombuffer(data, dtype=np.int16)
        if is_speech(frame, threshold):
            speech_start_frames += 1
            if speech_start_frames >= min_speech_frames:
                print("Recording!", flush=True)
                break
        else:
            speech_start_frames = 0

    voiced = [frame]
    silent_count = 0

    for _ in range(max_total_frames):
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        frame = np.frombuffer(data, dtype=np.int16)
        voiced.append(frame)
        if is_speech(frame, threshold):
            silent_count = 0
            print("█", end="", flush=True)
        else:
            silent_count += 1
            print("▁", end="", flush=True)
            if silent_count >= max_silent_frames:
                print("Silence detected", flush=True)
                break

    utterance = np.concatenate(voiced)

    if ENABLE_NOISE_REDUCTION and noise_profile is not None:
        print("Applying noise reduction...", end="", flush=True)
        utterance = apply_high_pass_filter(utterance, sample_rate=SAMPLE_RATE)
        utterance = spectral_subtraction_simple(utterance, noise_profile, NOISE_REDUCTION_STRENGTH)
        print(" Done!")

    return utterance



# ---------- MAIN LOOP (ELECTRON MODE) ----------
def main_electron():
    """Run in JSON-RPC mode for Electron"""
    import sys
    import json
    from backend.session import AssistantSession
    
    session = None
    
    try:
        session = AssistantSession()
        session.initialize()
        
        # Do NOT auto-start audio - wait for user command
        print("DEBUG: Initialized. Waiting for commands", flush=True)
        
        # Also read commands from stdin
        recording_thread = None
        
        for line in sys.stdin:
            try:
                cmd = json.loads(line.strip())
                command = cmd.get("command", "")
                print(f"DEBUG: Received command: {command}", flush=True)
                
                if command == "start":
                    if not session.running:
                        session.start_audio()
                elif command == "stop":
                    session.stop_audio()
                elif command == "shutdown":
                    session.shutdown()
                    break
                elif command == "status":
                    session.emit("status", {"state": "running"})
                elif command == "text_input":
                    text = cmd.get("data", "")
                    session.process_text(text)
                elif command == "start_audio":
                    # Initialize audio if not already done
                    if not session.running:
                        session.start_audio()
                    # Start manual recording in a thread (max 5 seconds)
                    recording_thread = threading.Thread(
                        target=lambda: session.record_manual(duration_sec=5.0),
                        daemon=True
                    )
                    recording_thread.start()
                elif command == "stop_audio":
                    # Stop recording by disabling audio
                    session.audio_active = False
                    if recording_thread:
                        recording_thread.join(timeout=1)
                elif command == "get_data":
                    data_type = cmd.get("data_type", "")
                    if data_type == "journal":
                        from brain.memory import get_journal
                        entries = get_journal()
                        session.emit("data_response", {"type": "journal", "data": entries})
                    elif data_type == "todos":
                        from brain.memory import list_todos
                        todos = list_todos()
                        session.emit("data_response", {"type": "todos", "data": todos})
                    elif data_type == "reminders":
                        from brain.memory import load_memory
                        data = load_memory()
                        session.emit("data_response", {"type": "reminders", "data": data.get("reminders", [])})
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}", flush=True)
            except Exception as e:
                print(f"DEBUG: Command error: {e}", flush=True)
                session.emit("error", {"message": str(e)})
                
    except KeyboardInterrupt:
        print("DEBUG: KeyboardInterrupt", flush=True)
    except Exception as e:
        print(json.dumps({"type": "error", "data": {"message": str(e)}}))
        import traceback
        print(traceback.format_exc(), flush=True)
    finally:
        if session:
            session.shutdown()

def main_cli():
    """Run in CLI mode (Kivy GUI)"""
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    
    print("VAANI - Nepali Voice Assistant")

    if not os.path.isdir(HF_NEPALI_MODEL_PATH):
        print("MODEL NOT FOUND")
        print(f"Expected location: {HF_NEPALI_MODEL_PATH}")
        print("Please run: python download_model.py")
        return

    try:
        p, stream = get_mic_stream()
        stt = NepaliSTT()
        tts = NepaliTTS()
        print("Audio devices initialized")
    except Exception as e:
        print(f"Initialization error: {e}")
        return

    threshold, noise_profile = calibrate_threshold(stream)

    greeting = "वाणी तयार छ।  म तपाईंलाई कसरी सहयोग गर्न सक्छु?"
    print(greeting)
    tts.speak(greeting)

    # Start Kivy GUI in parallel (optional)
    
    class VaaniApp(App):
        def build(self):
            layout = BoxLayout(orientation='vertical')
            self.input = TextInput(hint_text="Say something...")
            self.output = Label(text="Response here")
            btn = Button(text="Ask")
            btn.bind(on_press=self.ask)
            layout.add_widget(self.input)
            layout.add_widget(btn)
            layout.add_widget(self.output)
            return layout

        def ask(self, instance):
            text = self.input.text
            response = generate_reply(text)  # safe reply function
            self.output.text = response
    
    VaaniApp().run()

if __name__ == "__main__":
    try:
        # Print startup message first
        print("VAANI STARTUP", flush=True)
        sys.stdout.flush()
        
        # Check if running under Electron (look for stdin piped)
        try:
            is_piped = not sys.stdin.isatty()
        except:
            # If isatty() fails, assume we're under Electron
            is_piped = True
            
        if is_piped:
            # Running under Electron
            print("RUNNING UNDER ELECTRON MODE", flush=True)
            sys.stdout.flush()
            main_electron()
        else:
            # Running in CLI
            print("RUNNING IN CLI MODE", flush=True)
            sys.stdout.flush()
            main_cli()
    except Exception as e:
        print(f"FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
