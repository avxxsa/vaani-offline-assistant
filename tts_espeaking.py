import os
import subprocess
import tempfile
import winsound
import re
import wave
import array


class NepaliTTS:

    def __init__(
        self,
        exe_path=r"C:\Program Files\eSpeak NG\espeak-ng.exe",
        voice="ne+f4",       
        speed=150,          
        volume=170,         
        pitch=100,          
        gap=8,               
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

    def _auto_pause(self, t: str) -> str:
        
        words = t.split()
        if len(words) <= 4:
            return t

        out = []
        chunk = 0
        for w in words:
            out.append(w)
            chunk += 1
           
            if chunk >= 7:
                out.append("।")
                chunk = 0

        return " ".join(out)

    def preprocess_text(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""

        t = t.replace("VAANI", "वाणी").replace("vaani", "वाणी").replace("Vaani", "वाणी")
        t = re.sub(r"[^\u0900-\u097F a-zA-Z0-9।,?\s]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        t = self._auto_pause(t)

        return t

    def _soft_filter_wav_inplace(self, wav_path: str) -> None:
    
        if not self.smooth:
            return
        
        a = max(0.0, min(0.35, self.smooth_strength))
        if a <= 0:
            return

        try:
            with wave.open(wav_path, "rb") as wf:
                params = wf.getparams()
                frames = wf.readframes(params.nframes)

            
            if params.sampwidth != 2 or params.nchannels != 1:
                return

            samples = array.array("h")
            samples.frombytes(frames)

            # Two-pass smoothing for better results
            y = 0.0
            for i in range(len(samples)):
                x = float(samples[i])
                y = y + a * (x - y)
                samples[i] = int(max(-32768, min(32767, y)))

            y = 0.0
            for i in range(len(samples) - 1, -1, -1):
                x = float(samples[i])
                y = y + a * (x - y)
                samples[i] = int(max(-32768, min(32767, y)))

            with wave.open(wav_path, "wb") as wf:
                wf.setparams(params)
                wf.writeframes(samples.tobytes())

        except Exception:
            return

    def speak_to_wav(self, text: str, wav_path: str) -> bool:
        t = self.preprocess_text(text)
        if not t:
            return False

        cmd = [
            self.exe,
            "-v", self.voice,
            "-a", str(self.volume),
            "-s", str(self.speed),
            "-p", str(self.pitch),
            "-g", str(self.gap),
            "-w", wav_path,
            "--stdin",
        ]

        try:
            proc = subprocess.run(
                cmd,
                input=(t + "\n").encode("utf-8"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=20,
            )

            if proc.returncode != 0:
                return False
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
                return False

            self._soft_filter_wav_inplace(wav_path)
            return True

        except Exception as e:
            print(f"TTS generation error: {e}")
            return False

    def speak(self, text: str):
        wav_path = os.path.join(tempfile.gettempdir(), "vaani_tts.wav")

        ok = self.speak_to_wav(text, wav_path)
        if not ok:
            print("TTS failed (WAV not generated).")
            return

        try:
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        finally:
            try:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception:
                pass


if __name__ == "__main__":
    tts = NepaliTTS()
    tts.speak("नमस्ते म वाणी हुँ म तपाईंलाई कसरी सहयोग गर्न सक्छु आज मौसम कस्तो छ धन्यवाद फेरि भेटौँला")
import subprocess

def speak_text(text: str):
    print("🔊 Speaking:", text)
    subprocess.run([
        "espeak-ng",
        "-v", "ne",
        text
    ])
