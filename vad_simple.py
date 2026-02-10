import numpy as np


def frame_rms(audio_i16: np.ndarray) -> float:
<<<<<<< HEAD
<<<<<<< HEAD
    """Calculate RMS (Root Mean Square) of audio frame"""
=======
    # Root Mean Square (RMS) of audio frame
>>>>>>> origin/suprabha/speech-layer
=======
    # Root Mean Square (RMS) of audio frame
>>>>>>> origin/pratistha/ui
    x = audio_i16.astype(np.float32)
    return float((x * x).mean() ** 0.5 + 1e-9)


def is_speech(audio_i16: np.ndarray, threshold: float) -> bool:
<<<<<<< HEAD
<<<<<<< HEAD
    """Simple VAD based on RMS threshold"""
=======
    # Simple VAD based on RMS threshold
>>>>>>> origin/suprabha/speech-layer
=======
    # Simple VAD based on RMS threshold
>>>>>>> origin/pratistha/ui
    return frame_rms(audio_i16) >= threshold


def spectral_subtraction_simple(audio_i16: np.ndarray, noise_profile: np.ndarray, strength: float = 0.5) -> np.ndarray:
<<<<<<< HEAD
<<<<<<< HEAD
    """Simple noise reduction using spectral subtraction"""
=======
    # Simple noise reduction using spectral subtraction
>>>>>>> origin/suprabha/speech-layer
=======
    # Simple noise reduction using spectral subtraction
>>>>>>> origin/pratistha/ui
    if noise_profile is None or len(noise_profile) == 0:
        return audio_i16

    audio_f32 = audio_i16.astype(np.float32)
    noise_f32 = noise_profile.astype(np.float32)

    noise_rms = np.sqrt((noise_f32 * noise_f32).mean())
    audio_rms = np.sqrt((audio_f32 * audio_f32).mean())

    if audio_rms > noise_rms * 1.5:
        mask = np.abs(audio_f32) > (noise_rms * strength * 2)
        audio_f32 = audio_f32 * mask + audio_f32 * (1 - mask) * (1 - strength)

    audio_f32 = np.clip(audio_f32, -32768, 32767)
    return audio_f32.astype(np.int16)


def apply_high_pass_filter(audio_i16: np.ndarray, cutoff_hz: int = 80, sample_rate: int = 16000) -> np.ndarray:
<<<<<<< HEAD
<<<<<<< HEAD
    """Simple high-pass filter to remove low-frequency rumble/noise"""
=======
    # Simple high-pass filter to remove low-frequency rumble/noise
>>>>>>> origin/suprabha/speech-layer
=======
    # Simple high-pass filter to remove low-frequency rumble/noise
>>>>>>> origin/pratistha/ui
    audio_f32 = audio_i16.astype(np.float32)

    rc = 1.0 / (2 * np.pi * cutoff_hz)
    dt = 1.0 / sample_rate
    alpha = rc / (rc + dt)

    filtered = np.zeros_like(audio_f32)
    filtered[0] = audio_f32[0]

    for i in range(1, len(audio_f32)):
        filtered[i] = alpha * (filtered[i - 1] + audio_f32[i] - audio_f32[i - 1])

    filtered = np.clip(filtered, -32768, 32767)
    return filtered.astype(np.int16)