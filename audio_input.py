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
<<<<<<< HEAD
<<<<<<< HEAD
    return stream
=======
    return p, stream
>>>>>>> origin/suprabha/speech-layer
=======
    return p, stream
>>>>>>> origin/pratistha/ui
