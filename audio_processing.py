# audio_processing.py
from scipy.signal import butter, lfilter
import noisereduce as nr
import numpy as np

def bandpass_filter(data, lowcut=300, highcut=3400, fs=16000, order=5):

    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
    return lfilter(b, a, data)

def spectral_gating(audio, noise_sample):
    reduced = nr.reduce_noise(y=audio, y_noise=noise_sample, sr=16000, prop_decrease=1.0)
    return reduced

def normalize_audio(audio):
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    return audio
