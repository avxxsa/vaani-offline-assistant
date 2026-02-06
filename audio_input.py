import pyaudio
from config import SAMPLE_RATE, CHANNELS, FRAMES_PER_BUFFER

def get_mic_stream():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )
    stream.start_stream()
    return p, stream
