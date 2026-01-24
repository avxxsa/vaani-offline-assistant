import subprocess

def speak_text(text: str):
    print("🔊 Speaking:", text)
    subprocess.run([
        "espeak-ng",
        "-v", "ne",
        text
    ])