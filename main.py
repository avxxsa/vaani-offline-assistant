<<<<<<< HEAD
<<<<<<< HEAD
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from brain.brain import process_text

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
        response = process_text(text)
        self.output.text = response

VaaniApp().run()
=======
=======
>>>>>>> origin/pratistha/ui
import os
import numpy as np

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


def generate_reply(user_text: str) -> str:
    """Generate a reply based on user input"""
    t = (user_text or "").strip()
    t_lower = t.lower()

    # Exit keywords (Nepali and English)
    if ("बन्द" in t or "रोक" in t or
            "bye" in t_lower or "बाय" in t or
            "exit" in t_lower or "quit" in t_lower or "stop" in t_lower):
        return "ठिक छ। फेरि भेटौँला।"

    if "नमस्ते" in t or "हेलो" in t:
        return "नमस्ते।"

    if "धन्यवाद" in t:
        return "स्वागत छ।"

    if "तिम्रो नाम के हो" in t or "के हो तिम्रो नाम" in t:
        return "मेरो नाम वाणी हो।"

    return f"तपाईंले भन्नुभयो: {t}"


def main():
    """Main program loop"""
    if not os.path.isdir(HF_NEPALI_MODEL_PATH):
        print("MODEL NOT FOUND")
        print(f"Expected location: {HF_NEPALI_MODEL_PATH}")
        print("\nPlease run: python download_model.py")
        return

    print("VAANI - Nepali Voice Assistant")
    print(f"Model: {HF_NEPALI_MODEL_PATH}")
    print(f"Sample Rate: {SAMPLE_RATE} Hz")

    print("\nInitializing...")
    try:
        p, stream = get_mic_stream()
        print("Microphone stream opened")

        stt = NepaliSTT()
        print("STT model loaded")

        tts = NepaliTTS()
        print("TTS initialized")

    except Exception as e:
        print(f"Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return

    threshold, noise_profile = calibrate_threshold(stream)

    greeting = "वाणी तयार छ।  म तपाईंलाई कसरी सहयोग गर्न सक्छु?"
    print(f"\n{greeting}")
    tts.speak(greeting)

    print("\n")
    print("Ready! Speak in Nepali, pause to finish.")
    print("Say 'बन्द', 'रोक', or 'bye bye' to exit, or press Ctrl+C")
    print("\n")

    try:
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n Speak ")

                utterance = record_utterance(stream, threshold, noise_profile)

                print("Transcribing...", end="", flush=True)
                text = stt.transcribe_int16(utterance)
                print(" Done!")

                if not text:
                    print("No speech detected or transcription failed")
                    continue

                print(f"\nUser: {text}")

                reply = generate_reply(text)
                print(f"VAANI: {reply}")

                print("Speaking...", end="", flush=True)
                tts.speak(reply)
                print(" Done!")

                if "फेरि भेटौँला" in reply:
                    break



            except Exception as e:
                print(f"\nError in main loop: {e}")
                import traceback
                traceback.print_exc()
                continue

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        tts.speak("फेरि भेटौँला।")

    finally:
        print("Cleaning up.....")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Done!")


if __name__ == "__main__":
<<<<<<< HEAD
    main()
>>>>>>> origin/suprabha/speech-layer
=======
    main()
>>>>>>> origin/pratistha/ui
