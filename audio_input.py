import pyaudio
from config import SAMPLE_RATE, FRAMES_PER_BUFFER, CHANNELS

def get_mic_stream():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )
    return p, stream

def release_mic_stream(p, stream):
    if stream:
        stream.stop_stream()
        stream.close()
    if p:
        p.terminate()
