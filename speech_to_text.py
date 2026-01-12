from vosk import Model, KaldiRecognizer
import json
from config import sample_rate, vosk_model_path

class SpeechToText:
    def __init__(self):
        self.model = Model(vosk_model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)

    def listen(self, audio_bytes):
        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "")
        return ""
