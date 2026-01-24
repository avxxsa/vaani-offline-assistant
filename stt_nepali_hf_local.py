import numpy as np
import torch
from transformers import AutoProcessor, AutoModelForCTC
from config import HF_NEPALI_MODEL_PATH, SAMPLE_RATE, USE_GPU


class NepaliSTT:
    """Offline Nepali STT using Hugging Face wav2vec2 model"""

    def __init__(self):
        self.device = "cuda" if (USE_GPU and torch.cuda.is_available()) else "cpu"
        print(f"Loading STT model on device: {self.device}")
        self.processor = AutoProcessor.from_pretrained(HF_NEPALI_MODEL_PATH)
        self.model = AutoModelForCTC.from_pretrained(HF_NEPALI_MODEL_PATH).to(self.device)
        self.model.eval()

    def normalize_audio(self, audio_f32: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        max_val = np.abs(audio_f32).max()
        if max_val > 0:
            audio_f32 = audio_f32 / max_val * 0.95
        return audio_f32

    def remove_silence_edges(self, audio_f32: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Remove silence from start and end"""
        non_silent = np.abs(audio_f32) > threshold
        if not non_silent.any():
            return audio_f32

        first_sound = np.argmax(non_silent)
        last_sound = len(non_silent) - np.argmax(non_silent[::-1]) - 1

        padding = int(SAMPLE_RATE * 0.1)
        first_sound = max(0, first_sound - padding)
        last_sound = min(len(audio_f32), last_sound + padding)

        return audio_f32[first_sound:last_sound]

    @torch.no_grad()
    def transcribe_int16(self, audio_i16: np.ndarray) -> str:
        """Transcribe audio with preprocessing"""
        audio_f32 = audio_i16.astype(np.float32) / 32768.0

        audio_f32 = self.remove_silence_edges(audio_f32)
        audio_f32 = self.normalize_audio(audio_f32)

        min_samples = int(SAMPLE_RATE * 0.3)
        if len(audio_f32) < min_samples:
            return ""

        try:
            inputs = self.processor(
                audio_f32,
                sampling_rate=SAMPLE_RATE,
                return_tensors="pt",
                padding=True
            )
            input_values = inputs.input_values.to(self.device)

            logits = self.model(input_values).logits
            pred_ids = torch.argmax(logits, dim=-1)
            text = self.processor.batch_decode(pred_ids)[0]

            text = (text or "").strip()
            text = text.replace("[UNK]", "")
            text = text.replace("  ", " ")

            return text

        except Exception as e:
            print(f"Transcription error: {e}")
            return ""