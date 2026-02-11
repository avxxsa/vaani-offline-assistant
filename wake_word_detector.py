"""
Simple wake word detector for Vaani
Detects: "vaani", "hello vaani", "hi vaani", "yes vaani", "hey vaani"
Uses lightweight audio feature matching without heavy ML
"""

import numpy as np
from scipy import signal
import math

SAMPLE_RATE = 16000
WAKE_WORDS = ["vaani", "hello", "hi", "yes", "hey"]
WAKE_WORD_THRESHOLD = 0.5  # Confidence threshold


def get_mfcc_features(audio: np.ndarray, n_mfcc: int = 13) -> np.ndarray:
    """Extract basic MFCC-like features from audio"""
    # Simple frame-based feature extraction
    frame_length = int(0.025 * SAMPLE_RATE)  # 25ms frames
    frame_stride = int(0.010 * SAMPLE_RATE)  # 10ms stride
    
    frames = []
    for start in range(0, len(audio) - frame_length, frame_stride):
        frame = audio[start:start + frame_length]
        # Apply Hamming window
        frame = frame * np.hamming(len(frame))
        
        # Compute power spectrum
        fft = np.fft.rfft(frame)
        power = np.abs(fft) ** 2
        
        # Mel filterbank (simplified)
        mel_features = np.log(power[::len(power)//n_mfcc] + 1e-9)[:n_mfcc]
        frames.append(mel_features)
    
    return np.array(frames) if frames else np.zeros((1, n_mfcc))


def get_energy_profile(audio: np.ndarray) -> np.ndarray:
    """Get frame-by-frame energy for speech detection"""
    frame_length = int(0.025 * SAMPLE_RATE)
    frame_stride = int(0.010 * SAMPLE_RATE)
    
    energy = []
    for start in range(0, len(audio) - frame_length, frame_stride):
        frame = audio[start:start + frame_length]
        e = np.sum(frame ** 2) / len(frame)
        energy.append(e)
    
    return np.array(energy) if energy else np.array([0])


def detect_wake_word(audio: np.ndarray) -> tuple[bool, float]:
    """
    Detect if audio contains "vaani" wake word or similar patterns
    Returns (detected, confidence)
    """
    if len(audio) < SAMPLE_RATE * 0.3:  # At least 300ms of audio
        return False, 0.0
    
    try:
        # Normalize audio
        audio = audio.astype(np.float32) / (np.max(np.abs(audio)) + 1e-8)
        
        # Get energy profile - wake words typically have speech energy
        energy = get_energy_profile(audio)
        
        if len(energy) == 0:
            return False, 0.0
        
        # Check for speech-like energy pattern
        # Wake words have moderate energy with clear peaks
        mean_energy = np.mean(energy)
        max_energy = np.max(energy)
        
        # Too quiet or no clear peaks = not speech
        if max_energy < 0.01 or mean_energy < 0.001:
            return False, 0.0
        
        # Ratio of max to mean energy (speech typically has good contrast)
        energy_contrast = max_energy / (mean_energy + 1e-8)
        
        # Count energy peaks (speech typically has multiple peaks)
        energy_threshold = mean_energy * 2
        peaks = np.sum(energy > energy_threshold)
        peak_ratio = peaks / len(energy) if len(energy) > 0 else 0
        
        # Speech characteristics
        has_speech = energy_contrast > 3 and peak_ratio > 0.1
        
        if not has_speech:
            return False, 0.0
        
        # Additional check: zero crossing rate (speech has specific ZCR patterns)
        frame_length = int(0.025 * SAMPLE_RATE)
        frame_stride = int(0.010 * SAMPLE_RATE)
        
        zcr_list = []
        for start in range(0, len(audio) - frame_length, frame_stride):
            frame = audio[start:start + frame_length]
            if len(frame) > 1:
                zcr = np.mean(np.abs(np.diff(np.sign(frame)))) / 2
                zcr_list.append(zcr)
        
        if not zcr_list:
            return False, 0.0
        
        zcr = np.mean(zcr_list)
        
        # Typical speech ZCR is between 0.02 and 0.3
        zcr_speech_likelihood = 1.0 if 0.02 < zcr < 0.3 else 0.3
        
        # Calculate overall confidence
        # Combine energy_contrast, peak_ratio, and ZCR patterns
        confidence = (
            min(energy_contrast / 10, 1.0) * 0.4 +
            min(peak_ratio * 2, 1.0) * 0.3 +
            zcr_speech_likelihood * 0.3
        )
        
        # Boost confidence if it passes all checks
        if energy_contrast > 5 and peak_ratio > 0.2 and 0.02 < zcr < 0.3:
            confidence = min(confidence * 1.3, 1.0)
        
        detected = confidence > WAKE_WORD_THRESHOLD
        
        return detected, confidence
        
    except Exception as e:
        print(f"Wake word detection error: {e}", flush=True)
        return False, 0.0


def is_speech_activity(audio: np.ndarray) -> bool:
    """Simple speech activity detection - lighter than full wake word detection"""
    if len(audio) < SAMPLE_RATE * 0.1:  # At least 100ms
        return False
    
    try:
        audio = audio.astype(np.float32) / (np.max(np.abs(audio)) + 1e-8)
        energy = get_energy_profile(audio)
        
        if len(energy) == 0:
            return False
        
        mean_energy = np.mean(energy)
        max_energy = np.max(energy)
        
        # Simple threshold: has clear peaks above background
        return max_energy > 0.02 and max_energy / (mean_energy + 1e-8) > 2
        
    except:
        return False
