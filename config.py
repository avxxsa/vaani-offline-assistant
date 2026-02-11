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
ENABLE_NOISE_REDUCTION = True  # Disabled for speed and quality  
NOISE_REDUCTION_STRENGTH = 0.5
MIN_SPEECH_DURATION_SEC = 0.3

# Wake word settings
ENABLE_WAKE_WORD = True  # Require wake words like 'Vaani', 'Hello Vaani' to activate
WAKE_WORD_THRESHOLD = 0.5  # Confidence threshold for wake word detection (0.0-1.0)

# Paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# STT Model Configuration
# Using wav2vec2-nepali from HuggingFace (better quality for Nepali)
HF_NEPALI_MODEL_PATH = "anish-shilpakar/wav2vec2-nepali"  # Nepali-specific wav2vec2 model

# English model 
ENGLISH_MODEL_PATH = "openai/whisper-tiny"

# Compute
USE_GPU = False

# TTS Settings
TTS_ENGINE = "silero"  # "silero" (high quality) or "espeak" (lower quality)