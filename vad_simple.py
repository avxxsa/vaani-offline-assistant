import numpy as np


def frame_rms(audio_i16: np.ndarray) -> float:
    """Calculate RMS (Root Mean Square) of audio frame"""
    x = audio_i16.astype(np.float32)
    return float((x * x).mean() ** 0.5 + 1e-9)


def is_speech(audio_i16: np.ndarray, threshold: float) -> bool:
    """Simple VAD based on RMS threshold"""
    return frame_rms(audio_i16) >= threshold


def spectral_subtraction_simple(
    audio_i16: np.ndarray,
    noise_profile: np.ndarray,
    strength: float = 0.5
) -> np.ndarray:
    """Improved spectral subtraction for better noise reduction"""
    if noise_profile is None or len(noise_profile) == 0:
        return audio_i16

    audio_f32 = audio_i16.astype(np.float32)
    noise_f32 = noise_profile.astype(np.float32)

    noise_rms = np.sqrt((noise_f32 * noise_f32).mean() + 1e-8)
    audio_rms = np.sqrt((audio_f32 * audio_f32).mean() + 1e-8)

    # Less aggressive - preserve more signal
    if audio_rms > noise_rms * 1.1:  # Lowered threshold from 1.5 to 1.1
        # Use softer suppression to preserve speech
        gate_threshold = noise_rms * strength * 0.8  # Less aggressive gating
        mask = np.abs(audio_f32) > gate_threshold
        
        # Apply gentle attenuation instead of hard gate
        soft_factor = 0.5 + 0.5 * mask  # Ranges 0.5 to 1.0 (was 0.3 to 1.0)
        audio_f32 = audio_f32 * soft_factor
    else:
        # If audio is not much louder than background noise, it might be quiet speech
        # Apply gentle suppression instead of heavy attenuation
        audio_f32 = audio_f32 * 0.5

    audio_f32 = np.clip(audio_f32, -32768, 32767)
    return audio_f32.astype(np.int16)


def apply_high_pass_filter(
    audio_i16: np.ndarray,
    cutoff_hz: int = 80,
    sample_rate: int = 16000
) -> np.ndarray:
    """Simple high-pass filter to remove low-frequency rumble/noise"""
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


def apply_dynamic_range_compression(
    audio_i16: np.ndarray,
    threshold: float = 0.4,  # Relaxed from 0.3
    ratio: float = 1.5,  # Reduced from 2.0 - less aggressive
    sample_rate: int = 16000
) -> np.ndarray:
    """Apply dynamic range compression to normalize volume levels (gently)"""
    audio_f32 = audio_i16.astype(np.float32) / 32768.0
    
    # Apply RMS normalization in chunks
    chunk_size = int(sample_rate * 0.02)  # 20ms chunks
    compressed = np.zeros_like(audio_f32)
    
    for i in range(0, len(audio_f32), chunk_size):
        chunk = audio_f32[i:i+chunk_size]
        chunk_rms = np.sqrt((chunk * chunk).mean() + 1e-8)
        
        if chunk_rms > threshold:
            # Apply gentler gain reduction
            gain_reduction = 1.0 + (1.0 / ratio - 1.0) * (chunk_rms - threshold) / (1.0 - threshold)
            compressed[i:i+chunk_size] = chunk / gain_reduction
        else:
            compressed[i:i+chunk_size] = chunk
    
    # Normalize to use more of the full range (less aggressive)
    max_val = np.abs(compressed).max()
    if max_val > 0:
        compressed = compressed / max_val * 0.98  # Use 98% of range
    
    compressed = np.clip(compressed * 32768.0, -32768, 32767)
    return compressed.astype(np.int16)
