import numpy as np
from audio_input import *
from audio_processing import *
from speech_to_text import *
from text_to_speech import *
from config import sample_rate, channels, frames_per_buffer, noise_profile_sec

def main():
    stream = get_mic_stream()
    stt = SpeechToText()
    tts = TextToSpeech()

    noise_frames = []
    num_frames = int((noise_profile_sec * sample_rate) / frames_per_buffer)

    for i in range(num_frames):
        data = stream.read(frames_per_buffer, exception_on_overflow=False)
        frame = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        noise_frames.append(frame)

    noise_sample = np.concatenate(noise_frames)

    print("Vaani is listening...\n")

    while True:
        data=stream.read(frames_per_buffer, exception_on_overflow=False)
        audio=np.frombuffer(data, dtype=np.int16).astype(np.float32)

        audio=spectral_gating(audio, noise_sample)
        audio=bandpass_filter(audio)
        audio=normalize_audio(audio)

        pcm=(audio*32767).astype(np.int16)
        text=stt.listen(pcm.tobytes())

        if text:
            print("User:", text)

            if text.lower() in ["exit", "quit", "stop", "bye bye"]:
                tts.speak("ByeBye.\nTakecare.\nSeeya.")
                break

            tts.speak(text)

if __name__ == "__main__":
    main()