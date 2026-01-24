import os

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
FRAMES_PER_BUFFER = 4096

# VAD / utterance capture
NOISE_PROFILE_SEC = 1.0
SPEECH_THRESHOLD_MULTIPLIER = 2.5
END_SILENCE_SEC = 1.2
MAX_UTTERANCE_SEC = 15

# Noise reduction settings
ENABLE_NOISE_REDUCTION = True
NOISE_REDUCTION_STRENGTH = 0.5
MIN_SPEECH_DURATION_SEC = 0.3

# Paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
HF_NEPALI_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "wav2vec2-nepali")

# Compute
USE_GPU = False