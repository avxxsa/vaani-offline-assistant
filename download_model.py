from huggingface_hub import snapshot_download

MODEL_DIR = "models/wav2vec2-nepali"

print("Downloading Nepali Wav2Vec2 Model")
print(f"This will download ~300MB-1GB to: {MODEL_DIR}")
print("Please wait, this may take several minutes...\n")

try:
    path = snapshot_download(
        repo_id="anish-shilpakar/wav2vec2-nepali",
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False
    )

    print("MODEL DOWNLOADED SUCCESSFULLY!")
    print(f"Model saved to: {path}")
    print("\nYou can now run: python main.py")

except Exception as e:
    print("DOWNLOAD FAILED!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Make sure you have enough disk space (~2GB)")
    print("3. Try running: pip install --upgrade huggingface_hub")