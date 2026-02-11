"""
Nepali TTS using VITS model from Hugging Face
High quality, natural sounding Nepali speech synthesis
Completely offline, perfect for accessibility
"""

import torch
import scipy.io.wavfile
import tempfile
import os
import threading
import winsound
import sys

try:
    from transformers import VitsModel, AutoTokenizer
except ImportError:
    print("ERROR: transformers library not found. Install with: pip install transformers accelerate")
    raise


class VitsNepaliTTS:
    """High-quality offline Nepali TTS using VITS model"""
    
    def __init__(self, device="cpu"):
        self.device = device
        self.available = False
        self.model = None
        self.tokenizer = None
        self.playback_thread = None
        
        # Load model in background to avoid blocking
        load_thread = threading.Thread(target=self._load_model, daemon=False)
        load_thread.start()
    
    def _load_model(self):
        """Load VITS model (can take time on first run)"""
        try:
            print("DEBUG: Loading VITS Nepali TTS model...", flush=True)
            sys.stdout.flush()
            
            model_path = "atul10/nepali_male_v1"
            
            print("DEBUG: Loading tokenizer...", flush=True)
            sys.stdout.flush()
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            print("DEBUG: Tokenizer loaded", flush=True)
            sys.stdout.flush()
            
            print("DEBUG: Loading VITS model from HuggingFace (first run may take 2-3 minutes)...", flush=True)
            sys.stdout.flush()
            
            # Load model with explicit CPU
            self.model = VitsModel.from_pretrained(model_path)
            self.model.to("cpu")
            self.model.eval()
            
            print("DEBUG: VITS model loaded successfully!", flush=True)
            sys.stdout.flush()
            
            self.available = True
        except Exception as e:
            print(f"ERROR: Failed to load VITS model: {e}", flush=True)
            import traceback
            traceback.print_exc()
            self.available = False
    
    def _play_audio_async(self, wav_path: str):
        """Play audio file in background thread (non-blocking)"""
        try:
            print(f"DEBUG: Playing audio from {wav_path}...", flush=True)
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
            print(f"DEBUG: Audio playback complete", flush=True)
        except Exception as e:
            print(f"ERROR: Audio playback failed: {e}", flush=True)
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and validate text before VITS processing"""
        # Remove special characters that might cause tokenization issues
        text = text.replace("\n", " ").replace("\r", " ")
        text = " ".join(text.split())  # Normalize whitespace
        
        # Filter out problematic characters
        # Keep Nepali script and basic Latin
        filtered_chars = []
        for char in text:
            code = ord(char)
            # Allow Nepali script (2304-2431), Latin letters, numbers, and basic punctuation
            if (0x0900 <= code <= 0x097F or  # Devanagari (includes Nepali)
                0x0041 <= code <= 0x005A or  # A-Z
                0x0061 <= code <= 0x007A or  # a-z
                0x0030 <= code <= 0x0039 or  # 0-9
                code in (32, 45, 46, 44, 58, 59, 33, 63)):  # space, dash, period, comma, colon, semicolon, !, ?
                filtered_chars.append(char)
        
        return "".join(filtered_chars).strip()
    
    def speak(self, text: str):
        """Synthesize and play Nepali speech"""
        text = (text or "").strip()
        if not text:
            return
        
        # Preprocess text to avoid tokenization issues
        text = self._preprocess_text(text)
        if not text:
            print(f"DEBUG: Text empty after preprocessing", flush=True)
            return
        
        if not self.available:
            if self.model is None:
                print(f"DEBUG: VITS model still loading, please wait...", flush=True)
                # Wait for model to load (up to 5 minutes)
                import time
                for _ in range(300):  # 5 minutes with 1-second checks
                    time.sleep(1)
                    if self.available:
                        print(f"DEBUG: Model ready!", flush=True)
                        break
            
            if not self.available:
                print(f"DEBUG: VITS TTS not available ({len(text)} chars), falling back to eSpeak...", flush=True)
                self._fallback_to_espeaking(text)
                return
        
        try:
            print(f"DEBUG: VITS synthesizing {len(text)} characters", flush=True)
            sys.stdout.flush()
            
            # Tokenize input with error handling
            try:
                inputs = self.tokenizer(text, return_tensors="pt")
            except Exception as tokenize_error:
                print(f"DEBUG: Tokenization failed: {tokenize_error}, falling back to eSpeak", flush=True)
                self._fallback_to_espeaking(text)
                return
            
            # Check if inputs are valid
            if "input_ids" not in inputs or inputs["input_ids"].shape[1] == 0:
                print(f"DEBUG: Invalid tokenization result, falling back to eSpeak", flush=True)
                self._fallback_to_espeaking(text)
                return
            
            # Generate waveform
            with torch.no_grad():
                output = self.model(**inputs).waveform
            
            # Save to temporary WAV file with unique name
            import uuid
            wav_filename = f"vaani_tts_{uuid.uuid4().hex[:8]}.wav"
            wav_path = os.path.join(tempfile.gettempdir(), wav_filename)
            
            # Convert to numpy and save
            waveform_np = output.squeeze(0).cpu().numpy()
            wav_size = scipy.io.wavfile.write(
                wav_path, 
                self.model.config.sampling_rate, 
                (waveform_np * 32767).astype('int16')
            )
            
            print(f"DEBUG: WAV created successfully ({wav_size} bytes)", flush=True)
            sys.stdout.flush()
            
            # Play audio asynchronously
            self.playback_thread = threading.Thread(
                target=self._play_audio_async,
                args=(wav_path,),
                daemon=True
            )
            self.playback_thread.start()
            print(f"DEBUG: Audio playback started in background thread", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            print(f"ERROR: VITS TTS error: {e}", flush=True)
            print(f"DEBUG: Falling back to eSpeak for: {text[:50]}...", flush=True)
            self._fallback_to_espeaking(text)
    
    def _fallback_to_espeaking(self, text: str):
        """Fallback to eSpeak when VITS fails"""
        try:
            from tts_espeaking import NepaliTTS as EspeakTTS
            espeaking = EspeakTTS()
            if espeaking.available:
                print(f"DEBUG: Using eSpeak fallback for TTS", flush=True)
                espeaking.speak(text)
            else:
                print(f"WARNING: Both VITS and eSpeak TTS failed", flush=True)
        except Exception as fallback_error:
            print(f"ERROR: eSpeak fallback also failed: {fallback_error}", flush=True)


# Singleton instance
_tts = None

def get_tts_engine():
    """Get or create TTS instance"""
    global _tts
    if _tts is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _tts = VitsNepaliTTS(device=device)
    return _tts

def speak_text(text: str):
    """Compatibility function - tries VITS first, falls back to eSpeak"""
    tts = get_tts_engine()
    tts.speak(text)
