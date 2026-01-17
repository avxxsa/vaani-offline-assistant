import pyaudio
from config import sample_rate, channels, frames_per_buffer

def get_mic_stream():
    p=pyaudio.PyAudio()

    stream=p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frames_per_buffer
    )

    stream.start_stream()
    return stream