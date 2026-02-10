import torch
import numpy as np
from transformers import AutoProcessor, AutoModelForCTC
from config import SAMPLE_RATE, ENGLISH_MODEL_PATH, USE_GPU

class EnglishSTT:
    def __init__(self):
        self.device = "cuda" if (USE_GPU and torch.cuda.is_available()) else "cpu"
        print(f"Loading English STT model on device: {self.device}")
        try:
            self.processor = AutoProcessor.from_pretrained(ENGLISH_MODEL_PATH)
            self.model = AutoModelForCTC.from_pretrained(ENGLISH_MODEL_PATH).to(self.device)
            self.model.eval()
            self.available = True
        except Exception as e:
            print(f"English model not found or invalid at {ENGLISH_MODEL_PATH}: {e}")
            self.available = False

    def transcribe_int16(self, audio_i16: np.ndarray) -> str:
        if not self.available:
            return ""

        audio_f32 = audio_i16.astype(np.float32) / 32768.0
        
        # Simple normalization
        max_val = np.abs(audio_f32).max()
        if max_val > 0:
            audio_f32 = audio_f32 / max_val * 0.95

        try:
            inputs = self.processor(
                audio_f32,
                sampling_rate=SAMPLE_RATE,
                return_tensors="pt",
                padding=True
            )
            input_values = inputs.input_values.to(self.device)

            with torch.no_grad():
                logits = self.model(input_values).logits
            
            pred_ids = torch.argmax(logits, dim=-1)
            text = self.processor.batch_decode(pred_ids)[0]
            return text.lower().strip()

        except Exception as e:
            print(f"English transcription error: {e}")
            return ""

