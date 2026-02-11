"""
Fast local speech-to-text using Vosk
No downloads needed - uses pre-installed Vosk model
"""

import json
import os
import numpy as np
from vosk import Model, KaldiRecognizer
from config import SAMPLE_RATE, VOSK_MODEL_PATH


class VoskSTT:
    """Fast local STT using Vosk - works immediately without downloads"""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = VOSK_MODEL_PATH
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at: {model_path}")
        
        print(f"Loading Vosk model from: {model_path}", flush=True)
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        print("Vosk STT ready!", flush=True)
    
    def transcribe_int16(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio data (int16 format)
        Vosk expects audio to be fed in chunks
        
        Args:
            audio_data: numpy array of int16 audio samples
            
        Returns:
            Transcribed text string
        """
        if len(audio_data) == 0:
            return ""
        
        try:
            # Reset recognizer for new utterance
            self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
            
            # Convert to bytes
            audio_bytes = audio_data.astype(np.int16).tobytes()
            
            # Feed audio in chunks to Vosk (recommended chunk size: 4096 samples = ~256ms)
            chunk_size = 4096 * 2  # 2 bytes per sample (int16)
            final_result = ""
            
            for i in range(0, len(audio_bytes), chunk_size):
                chunk = audio_bytes[i:i + chunk_size]
                
                if self.recognizer.AcceptWaveform(chunk):
                    # Got a final result
                    result_json = self.recognizer.Result()
                    result = json.loads(result_json)
                    words = result.get("result", [])
                    
                    if words:
                        text = " ".join([w.get("result", "") for w in words])
                        final_result += text + " "
            
            # Get any remaining final result
            final_json = self.recognizer.FinalResult()
            final = json.loads(final_json)
            words = final.get("result", [])
            if words:
                text = " ".join([w.get("result", "") for w in words])
                final_result += text
            
            return final_result.strip()
            
        except Exception as e:
            print(f"Error during Vosk transcription: {e}", flush=True)
            return ""

