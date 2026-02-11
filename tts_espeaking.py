import os
import subprocess
import tempfile
import re
import wave
import array
import shutil
import threading

# Optional: winsound only exists on Windows
try:
    import winsound
except ImportError:
    winsound = None

from nepali_transliterate import transliterate_nepali_to_latin, is_nepali_text


class NepaliTTS:
    def __init__(
        self,
        exe_path="espeak-ng",
        voice="ne",
        speed=110,  # Slower for natural speech (was 150)
        volume=200,  # Slightly louder (was 170)
        pitch=60,    # Lower pitch for more natural tone (was 100)
        gap=12,      # More gap between words (was 8)
        smooth=True,
        smooth_strength=0.25
    ):
        self.exe = exe_path
        self.voice = voice
        self.speed = speed
        self.volume = volume
        self.pitch = pitch
        self.gap = gap
        self.smooth = smooth
        self.smooth_strength = float(smooth_strength)
        self.playback_thread = None  # Track playback thread
        
        # Check if espeak-ng exists
        self.available = shutil.which(self.exe) is not None
        if not self.available:
            print(f"WARNING: {self.exe} not found. TTS will be disabled.", flush=True)

    def add_prosody_hints(self, text: str) -> str:
        """
        Add prosody hints to text for more natural speech.
        Breaks long sentences and adds emphasis markers.
        """
        # Add comma pauses for sentence structure
        text = text.replace('।', ',')  # Nepali danda -> comma for pause
        # Add subtle pauses after punctuation
        text = re.sub(r'([!?।\.,])', r'\1 ', text)
        return text
    
    def preprocess_text(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        # Normalize whitespace
        t = re.sub(r"\s+", " ", t)
        # Add prosody hints for natural speech
        t = self.add_prosody_hints(t)
        return t
    
    def _play_audio_async(self, wav_path: str):
        """Play audio file in background thread (non-blocking)"""
        try:
            print(f"DEBUG: Playing audio from {wav_path}...", flush=True)
            if winsound is not None:
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                print(f"DEBUG: Audio playback complete", flush=True)
        except Exception as e:
            print(f"ERROR: Audio playback failed: {e}", flush=True)

    def speak(self, text: str, force_voice: str = None):
        if not self.available:
            print(f"[SPEAK] ({len(text)} chars)", flush=True)
            return
        
        text = self.preprocess_text(text)
        if not text:
            return
            
        try:
            # Detect language and select appropriate voice
            voice_to_use = force_voice or self.voice
            
            if is_nepali_text(text):
                # Use Nepali voice for Nepali text (no transliteration needed)
                voice_to_use = "ne"
                print(f"DEBUG: Speaking Nepali text with voice 'ne'", flush=True)
            else:
                # Use English voice for English text
                voice_to_use = "en"
            
            print(f"DEBUG: TTS Speaking in voice '{voice_to_use}': {len(text)} chars", flush=True)
            
            # On Windows, use winsound to play audio
            if winsound is not None:
                # Generate unique WAV path to avoid race conditions with concurrent calls
                import uuid
                wav_filename = f"vaani_tts_{uuid.uuid4().hex[:8]}.wav"
                wav_path = os.path.join(tempfile.gettempdir(), wav_filename)
                print(f"DEBUG: Generating WAV at {wav_path}", flush=True)
                
                # Build command with appropriate voice and natural speech parameters
                cmd = [
                    self.exe,
                    "-v", voice_to_use,  # Voice: "ne" for Nepali, "en" for English
                    "-s", str(self.speed),  # Speed (slower = more natural)
                    "-a", str(self.volume),  # Amplitude/volume
                    "-p", str(self.pitch),  # Pitch (lower = more natural)
                    "-g", str(self.gap),  # Gap between words (more = clearer)
                    "-w", wav_path,  # Output WAV file
                    text  # Text to speak (transliterated if Nepali)
                ]
                
                print(f"DEBUG: espeak-ng command: {' '.join(cmd[:6])}... ({len(text)} chars)", flush=True)
                result = subprocess.run(cmd, check=True, timeout=15, capture_output=True, text=True)
                
                # Check if WAV file was created
                if not os.path.exists(wav_path):
                    print(f"ERROR: WAV file not created at {wav_path}", flush=True)
                    if result.stderr:
                        print(f"STDERR: {result.stderr}", flush=True)
                    return
                
                wav_size = os.path.getsize(wav_path)
                if wav_size == 0:
                    print(f"ERROR: WAV file is empty", flush=True)
                    if result.stderr:
                        print(f"STDERR: {result.stderr}", flush=True)
                    return
                
                print(f"DEBUG: WAV created successfully ({wav_size} bytes)", flush=True)
                
                # Play audio asynchronously in background thread to avoid freezing
                self.playback_thread = threading.Thread(
                    target=self._play_audio_async,
                    args=(wav_path,),
                    daemon=True
                )
                self.playback_thread.start()
                print(f"DEBUG: Audio playback started in background thread", flush=True)
            else:
                # Fallback: use subprocess directly (non-Windows)
                print(f"DEBUG: Using subprocess for TTS (non-Windows)", flush=True)
                subprocess.run([
                    self.exe,
                    "-v", self.voice,
                    "-s", str(self.speed),
                    text
                ], check=True, timeout=15)
                
        except Exception as e:
            print(f"TTS error: {e}", flush=True)
            import traceback
            traceback.print_exc()



# ✅ COMPATIBILITY FUNCTION
# This keeps your existing code working
_tts = NepaliTTS()

def speak_text(text: str):
    print("🔊 Speaking:", text)
    _tts.speak(text)
