import json
import sys
import threading
import time
import numpy as np
import traceback
from queue import Queue, Empty

from audio_input import get_mic_stream, release_mic_stream
from vad_simple import is_speech, apply_high_pass_filter, spectral_subtraction_simple, frame_rms
from stt_nepali_hf_local import NepaliSTT
from speech_to_text import EnglishSTT
from tts_espeaking import NepaliTTS
from brain.brain import process_text
from config import (
    SAMPLE_RATE, FRAMES_PER_BUFFER, NOISE_PROFILE_SEC,
    SPEECH_THRESHOLD_MULTIPLIER, MIN_SPEECH_DURATION_SEC,
    MAX_UTTERANCE_SEC, END_SILENCE_SEC, NOISE_REDUCTION_STRENGTH, 
    ENABLE_NOISE_REDUCTION
)

class AssistantSession:
    def __init__(self):
        self.running = False
        self.listening = False
        self.transcribing = False
        self.speaking = False
        
        self.stt = None
        self.stt_ne = None # Cache models
        self.stt_en = None
        self.current_lang = "ne" # 'ne' or 'en'
        
        self.tts = None
        self.mic_stream = None
        self.py_audio = None
        self.audio_queue = Queue()
        
        # Audio processing state
        self.threshold = 500  # Default, will calibrate
        self.noise_profile = None
        
        # Threads
        self.listen_thread = None
        self.process_thread = None

    def emit(self, event_type: str, data: dict = None):
        """Emit a JSON event to stdout"""
        msg = {"type": event_type, "data": data or {}}
        print(json.dumps(msg), flush=True)

    def initialize(self):
        """Load models and hardware"""
        print("DEBUG: Calling initialize()", flush=True)
        self.emit("status", {"state": "Initializing", "message": "Loading models..."})
        try:
            # We lazy load models when switching or load both now? 
            # Let's load Nepali by default as it is the main one.
            print("DEBUG: Loading default language (ne)", flush=True)
            self.set_language("ne")
            print("DEBUG: Initializing TTS", flush=True)
            self.tts = NepaliTTS() # Generic TTS wrapper would be better but keeping simple
            print("DEBUG: Models loaded successfully", flush=True)
            self.emit("status", {"state": "Ready", "message": "Models loaded"})
        except Exception as e:
            msg = f"Model load failed: {str(e)}"
            print(f"DEBUG: {msg}", flush=True)
            self.emit("error", {"message": msg})
            traceback.print_exc()
            raise

    def set_language(self, lang: str):
        self.current_lang = lang
        try:
            if lang == "ne":
                if not self.stt_ne:
                    self.stt_ne = NepaliSTT()
                self.stt = self.stt_ne
            elif lang == "en":
                if not self.stt_en:
                    self.stt_en = EnglishSTT()
                self.stt = self.stt_en
            self.emit("status", {"state": "LanguageChanged", "message": f"Language set to {lang}"})
        except Exception as e:
            self.emit("error", {"message": f"Failed to switch language: {e}"})

    def start_audio(self):
        """Start microphone and processing threads"""
        if self.running:
            return

        try:
            self.py_audio, self.mic_stream = get_mic_stream()
            self.running = True
            
            # Calibrate first
            self.emit("status", {"state": "Calibrating", "message": "Calibrating background noise..."})
            self.calibrate_noise()
            self.emit("status", {"state": "Idle", "message": "Listening..."})

            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
            
            self.listen_thread.start()
            self.process_thread.start()
            
        except Exception as e:
             self.emit("error", {"message": f"Audio start failed: {str(e)}"})
             traceback.print_exc()

    def calibrate_noise(self):
        """Quick calibration of noise profile"""
        frames = []
        num_frames = int((NOISE_PROFILE_SEC * SAMPLE_RATE) / FRAMES_PER_BUFFER)
        
        for _ in range(num_frames):
            try:
                data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frame = np.frombuffer(data, dtype=np.int16)
                frames.append(frame)
            except Exception:
                pass
            
        if frames:
            noise_sample = np.concatenate(frames)
            self.threshold = frame_rms(noise_sample) * SPEECH_THRESHOLD_MULTIPLIER
            self.noise_profile = noise_sample
            
            self.emit("debug", {
                "threshold": float(self.threshold),
                "rms": float(frame_rms(noise_sample))
            })
        else:
             self.emit("error", {"message": "Calibration failed: No audio data"})

    def _listen_loop(self):
        """Reads audio from mic and detects VAD segments"""
        while self.running:
            if self.speaking:
                time.sleep(0.1)
                continue
                
            try:
                self._record_single_utterance()
            except Exception as e:
                self.emit("error", {"message": f"Listen error: {str(e)}"})
                traceback.print_exc()
                time.sleep(1)

    def _record_single_utterance(self):
        """Records one utterance and pushes to queue"""
        # Wait for speech start
        speech_frames = 0
        min_speech_frames = int(MIN_SPEECH_DURATION_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
        
        while self.running and not self.speaking:
            try:
                data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frame = np.frombuffer(data, dtype=np.int16)
            except Exception:
                continue

            if is_speech(frame, self.threshold):
                speech_frames += 1
                if speech_frames >= min_speech_frames:
                    self.emit("status", {"state": "Listening", "message": "Listening..."})
                    break
            else:
                speech_frames = 0
        
        if not self.running: return

        # Record until silence
        voiced_frames = [frame] 
        max_silent_frames = int(END_SILENCE_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
        silent_count = 0
        
        while self.running:
            try:
                data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frame = np.frombuffer(data, dtype=np.int16)
            except Exception:
                break
                
            voiced_frames.append(frame)
            
            if is_speech(frame, self.threshold):
                silent_count = 0
            else:
                silent_count += 1
                if silent_count >= max_silent_frames:
                    break
        
        # Push complete utterance
        if len(voiced_frames) > min_speech_frames:
            audio_data = np.concatenate(voiced_frames)
            self.audio_queue.put(audio_data)
            self.emit("status", {"state": "Processing", "message": "Processing..."})

    def _process_loop(self):
        """Consumes audio queue, transcribes, and executes"""
        while self.running:
            try:
                audio = self.audio_queue.get(timeout=1)
            except Empty:
                continue

            # Noise Reduction
            if ENABLE_NOISE_REDUCTION and self.noise_profile is not None:
                audio = apply_high_pass_filter(audio, sample_rate=SAMPLE_RATE)
                audio = spectral_subtraction_simple(audio, self.noise_profile, NOISE_REDUCTION_STRENGTH)

            # Transcribe
            text = self.stt.transcribe_int16(audio)
            
            if not text:
                self.emit("status", {"state": "Idle", "message": "Listening..."})
                continue
                
            self.emit("transcript", {"text": text, "is_final": True})
            
            # Process text
            response_text = process_text(text)
            self.emit("response", {"text": response_text})
            
            # TTS
            self.speaking = True
            self.emit("status", {"state": "Speaking", "message": "Speaking..."})
            self.tts.speak(response_text)
            self.speaking = False
            self.emit("status", {"state": "Idle", "message": "Listening..."})

    def stop(self):
        self.running = False
        if self.mic_stream:
            release_mic_stream(self.py_audio, self.mic_stream)
        self.emit("status", {"state": "Stopped", "message": "Assistant stopped"})
