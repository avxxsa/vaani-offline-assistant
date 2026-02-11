"""
LLM-based response generation using Ollama + Gemma 3 1B
Provides intelligent conversation responses in English and Nepali
"""

import requests
import json
import sys
import re
from typing import Optional

# Ollama server configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma2:2b"  # Lightweight 2B model - replace with gemma:1b once available
OLLAMA_TIMEOUT = 20  # seconds (reduced from 30 to avoid long hangs)

def remove_emojis(text: str) -> str:
    """Remove emoji characters that cause Windows console encoding errors"""
    if not text:
        return text
    # Remove emoji and other Unicode characters that Windows can't handle
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    return text.strip()

def is_ollama_available() -> bool:
    """Check if Ollama server is running and model is available"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [m.get('name', '').split(':')[0] for m in data.get('models', [])]
            is_available = any('gemma' in m for m in models)
            if is_available:
                print(f"DEBUG: Ollama is available with Gemma model", flush=True)
            return is_available
    except Exception as e:
        print(f"DEBUG: Ollama not available: {e}", flush=True)
    return False

def generate_response(user_text: str, is_nepali: bool = True) -> Optional[str]:
    """
    Generate intelligent response using Ollama Gemma 3 1B model
    
    Args:
        user_text: User's input text
        is_nepali: Whether response should be in Nepali
    
    Returns:
        Generated response text or None if LLM unavailable
    """
    try:
        # Build the prompt
        if is_nepali:
            system_prompt = """तपाई एक सहायक भॉइस असिस्ट्यान्ट हुनुहुन्छ जसको नाम वाणी हो।
तपाई नेपाली भाषामा छोटो, मित्रतापूर्ण र उपयोगी जवाफ दिनुहुन्छ।
जवाफ ३०० शब्द भन्दा कम होनु चाहिए।
तपाईं सदा नेपाली भाषामा जवाफ दिनुहुन्छ।"""
        else:
            system_prompt = """You are a voice assistant named Vaani.
Provide short, friendly, and helpful responses in English.
Keep responses under 100 words.
Always respond in English."""
        
        prompt = f"{system_prompt}\n\nUser: {user_text}\nAssistant:"
        
        # Call Ollama API
        print(f"DEBUG: Sending request to Ollama for Gemma response", flush=True)
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 150  # Max tokens for fast response
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get('response', '').strip()
            
            if generated_text:
                # Remove emojis that cause Windows encoding errors
                generated_text = remove_emojis(generated_text)
                print(f"DEBUG: Ollama generated response: {len(generated_text)} chars", flush=True)
                return generated_text
        else:
            print(f"DEBUG: Ollama error {response.status_code}: {response.text}", flush=True)
            
    except requests.exceptions.Timeout:
        print(f"DEBUG: Ollama request timeout after {OLLAMA_TIMEOUT}s", flush=True)
    except requests.exceptions.ConnectionError:
        print(f"DEBUG: Cannot connect to Ollama at {OLLAMA_HOST}", flush=True)
    except Exception as e:
        print(f"DEBUG: LLM error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    return None


if __name__ == "__main__":
    # Test the LLM
    print("Testing Ollama Gemma integration...")
    
    if is_ollama_available():
        print("\n✓ Ollama is available")
        
        # Test English response
        print("\n--- English Test ---")
        response = generate_response("What is your name?", is_nepali=False)
        if response:
            print(f"Response: {response}")
        else:
            print("No response generated")
        
        # Test Nepali response
        print("\n--- Nepali Test ---")
        response = generate_response("तपाईंको नाम के हो?", is_nepali=True)
        if response:
            print(f"Response: {response}")
        else:
            print("No response generated")
    else:
        print("\n✗ Ollama is NOT available")
        print("\nTo install Ollama:")
        print("1. Download from https://ollama.ai")
        print("2. Run in PowerShell:")
        print("   ollama serve")
        print("3. In another terminal:")
        print("   ollama pull gemma:1b")
