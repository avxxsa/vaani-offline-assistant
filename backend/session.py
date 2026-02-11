import json
import sys
import threading
import time
import numpy as np
import traceback
from queue import Queue, Empty

from audio_input import get_mic_stream, release_mic_stream
from vad_simple import is_speech, apply_high_pass_filter, spectral_subtraction_simple, frame_rms, apply_dynamic_range_compression
from stt_nepali_hf_local import NepaliSTT
from speech_to_text import EnglishSTT
from tts_vits_nepali import VitsNepaliTTS
from wake_word_detector import detect_wake_word
from brain.brain import process_text
from config import (
    SAMPLE_RATE, FRAMES_PER_BUFFER, NOISE_PROFILE_SEC,
    SPEECH_THRESHOLD_MULTIPLIER, MIN_SPEECH_DURATION_SEC,
    MAX_UTTERANCE_SEC, END_SILENCE_SEC, NOISE_REDUCTION_STRENGTH, 
    ENABLE_NOISE_REDUCTION, ENABLE_WAKE_WORD
)

class AssistantSession:
    def __init__(self):
        self.running = False
        self.listening = False
        self.transcribing = False
        self.speaking = False
        self.audio_active = False  # Track if audio should be recording
        
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
            print("DEBUG: Initializing VITS TTS", flush=True)
            self.tts = VitsNepaliTTS()
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
                    print("Loading Nepali STT...", flush=True)
                    self.stt_ne = NepaliSTT()
                self.stt = self.stt_ne
            elif lang == "en":
                if not self.stt_en:
                    self.stt_en = EnglishSTT()
                self.stt = self.stt_en
            self.emit("status", {"state": "LanguageChanged", "message": f"Language set to {lang}"})
        except Exception as e:
            error_msg = f"Failed to switch language: {e}"
            print(f"ERROR: {error_msg}", flush=True)
            traceback.print_exc()
            self.emit("error", {"message": error_msg})
            raise

    def start_audio(self):
        """Start microphone and processing threads"""
        if self.running:
            # Audio already running, just enable listening
            self.audio_active = True
            wait_msg = "Waiting for wake word..." if ENABLE_WAKE_WORD else "Listening..."
            self.emit("status", {"state": "Idle", "message": wait_msg})
            return

        try:
            self.py_audio, self.mic_stream = get_mic_stream()
            self.running = True
            self.audio_active = True
            
            # Calibrate first
            self.emit("status", {"state": "Calibrating", "message": "Calibrating background noise..."})
            self.calibrate_noise()
            
            wait_msg = "Waiting for wake word..." if ENABLE_WAKE_WORD else "Listening..."
            self.emit("status", {"state": "Idle", "message": wait_msg})

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
        """Reads audio from mic, detects wake words, then records utterances"""
        while self.running:
            if self.speaking or not self.audio_active:
                time.sleep(0.1)
                continue
                
            try:
                # Stage 1: Wait for wake word (if enabled)
                if ENABLE_WAKE_WORD:
                    self._listen_for_wake_word()
                
                # Stage 2: Record full utterance
                if self.running and self.audio_active:
                    self._record_single_utterance()
            except Exception as e:
                self.emit("error", {"message": f"Listen error: {str(e)}"})
                traceback.print_exc()
                time.sleep(1)

    def _listen_for_wake_word(self):
        """Listen for wake words like 'vaani', 'hello vaani', 'hi vaani', etc"""
        wake_word_buffer = []
        buffer_duration = 1.0  # 1 second buffer for wake word detection
        buffer_frames = int(buffer_duration * SAMPLE_RATE / FRAMES_PER_BUFFER)
        
        self.emit("status", {"state": "Idle", "message": "Waiting for wake word (say 'Vaani', 'Hello Vaani', 'Hi Vaani')..."})
        
        while self.running and self.audio_active and not self.speaking:
            try:
                data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frame = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                wake_word_buffer.append(frame)
                
                # Keep buffer at fixed size
                if len(wake_word_buffer) > buffer_frames:
                    wake_word_buffer.pop(0)
                
                # Check for wake word when we have enough audio
                if len(wake_word_buffer) == buffer_frames:
                    audio_chunk = np.concatenate(wake_word_buffer)
                    detected, confidence = detect_wake_word(audio_chunk)
                    
                    if detected:
                        self.emit("wake_word", {"confidence": float(confidence)})
                        self.emit("status", {"state": "Active", "message": "Wake word detected! Listening..."})
                        print(f"DEBUG: Wake word detected with confidence: {confidence:.2f}", flush=True)
                        return  # Exit wake word listening, start full recording
                        
            except Exception:
                continue

    def _record_single_utterance(self):
        """Records one utterance and pushes to queue"""
        # Wait for speech start
        speech_frames = 0
        min_speech_frames = int(MIN_SPEECH_DURATION_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
        
        while self.running and self.audio_active and not self.speaking:
            try:
                data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frame = np.frombuffer(data, dtype=np.int16)
            except Exception:
                continue

            if is_speech(frame, self.threshold):
                speech_frames += 1
                if speech_frames >= min_speech_frames:
                    self.emit("status", {"state": "Listening", "message": "Recording your message..."})
                    break
            else:
                speech_frames = 0
        
        if not self.running or not self.audio_active: 
            return

        # Record until silence
        voiced_frames = [frame] 
        max_silent_frames = int(END_SILENCE_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
        silent_count = 0
        max_recording_frames = int(MAX_UTTERANCE_SEC * SAMPLE_RATE / FRAMES_PER_BUFFER)
        recording_frames = 1
        
        while self.running and self.audio_active and recording_frames < max_recording_frames:
            try:
                data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frame = np.frombuffer(data, dtype=np.int16)
            except Exception:
                break
                
            voiced_frames.append(frame)
            recording_frames += 1
            
            if is_speech(frame, self.threshold):
                silent_count = 0
            else:
                silent_count += 1
                if silent_count >= max_silent_frames:
                    break
        
        # Push complete utterance (require minimum speech)
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

            # Safety check: ensure STT is initialized
            if self.stt is None:
                self.emit("error", {"message": "STT model not initialized"})
                continue

            # Comprehensive audio preprocessing
            if ENABLE_NOISE_REDUCTION and self.noise_profile is not None:
                print("Applying noise reduction...", flush=True)
                audio = apply_high_pass_filter(audio, sample_rate=SAMPLE_RATE)
                audio = spectral_subtraction_simple(audio, self.noise_profile, NOISE_REDUCTION_STRENGTH)
                audio = apply_dynamic_range_compression(audio, sample_rate=SAMPLE_RATE)

            # Transcribe
            print("Starting transcription...", flush=True)
            text = self.stt.transcribe_int16(audio)
            print(f"Got transcription result: {len(text)} chars", flush=True)
            
            if not text:
                wait_msg = "Waiting for wake word..." if ENABLE_WAKE_WORD else "Listening..."
                self.emit("status", {"state": "Idle", "message": wait_msg})
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
            wait_msg = "Waiting for wake word..." if ENABLE_WAKE_WORD else "Listening..."
            self.emit("status", {"state": "Idle", "message": wait_msg})

    def stop_audio(self):
        """Stop audio listening (but keep backend running)"""
        self.audio_active = False
        self.emit("status", {"state": "Idle", "message": "Waiting for input..."})
    
    def record_manual(self, duration_sec: float = 5.0):
        """Manually record audio for a fixed duration (used for hold-to-speak)"""
        if not self.mic_stream:
            self.emit("error", {"message": "Audio not initialized"})
            return
        
        self.emit("status", {"state": "Listening", "message": "Recording..."})
        
        frames = []
        num_frames = int((duration_sec * SAMPLE_RATE) / FRAMES_PER_BUFFER)
        
        try:
            for i in range(num_frames):
                try:
                    data = self.mic_stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                    frame = np.frombuffer(data, dtype=np.int16)
                    frames.append(frame)
                    
                    # Visual feedback every second
                    if (i + 1) % (SAMPLE_RATE // FRAMES_PER_BUFFER) == 0:
                        elapsed = (i + 1) * FRAMES_PER_BUFFER / SAMPLE_RATE
                        print(f"DEBUG: Recording {elapsed:.1f}s", flush=True)
                except Exception as e:
                    print(f"DEBUG: Read error: {e}", flush=True)
                    break
        except KeyboardInterrupt:
            pass
        
        if frames and len(frames) > 1:
            audio_data = np.concatenate(frames)
            
            # Apply comprehensive audio preprocessing
            if ENABLE_NOISE_REDUCTION and self.noise_profile is not None:
                print(f"DEBUG: Applying audio preprocessing to {len(audio_data)} samples", flush=True)
                
                # Step 1: High-pass filter to remove rumble
                audio_data = apply_high_pass_filter(audio_data, sample_rate=SAMPLE_RATE)
                
                # Step 2: Spectral subtraction for noise reduction
                audio_data = spectral_subtraction_simple(audio_data, self.noise_profile, NOISE_REDUCTION_STRENGTH)
                
                # Step 3: Dynamic range compression for volume normalization
                audio_data = apply_dynamic_range_compression(audio_data, sample_rate=SAMPLE_RATE)
            
            self.audio_queue.put(audio_data)
            self.emit("status", {"state": "Processing", "message": "Processing..."})
            print(f"DEBUG: Recorded {len(audio_data)} samples, queued for processing", flush=True)
        else:
            self.emit("error", {"message": "No audio recorded"})

    
    def shutdown(self):
        """Completely shut down the assistant"""
        self.running = False
        self.audio_active = False
        if self.mic_stream:
            release_mic_stream(self.py_audio, self.mic_stream)
        self.emit("status", {"state": "Stopped", "message": "Assistant stopped"})
    
    def process_text(self, text: str):
        """Process user text input"""
        try:
            self.emit("status", {"state": "Processing", "message": "Processing..."})
            response_text = process_text(text)
            print(f"DEBUG: response_text length = {len(response_text)}", flush=True)
            self.emit("response", {"text": response_text})
            
            # TTS
            self.speaking = True
            self.emit("status", {"state": "Speaking", "message": "Speaking..."})
            print(f"DEBUG: About to call tts.speak()", flush=True)
            self.tts.speak(response_text)
            self.speaking = False
            self.emit("status", {"state": "Idle", "message": "Listening..."})
        except Exception as e:
            print(f"DEBUG: Exception in process_text: {type(e).__name__}: {e}", flush=True)
            self.emit("error", {"message": f"Processing error: {str(e)}"})

    def stop(self):
        self.running = False
        if self.mic_stream:
            release_mic_stream(self.py_audio, self.mic_stream)
        self.emit("status", {"state": "Stopped", "message": "Assistant stopped"})
