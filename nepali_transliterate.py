"""
Simple Nepali Devanagari to Latin transliteration for TTS
Maps Nepali characters to phonetic Latin equivalents that espeak-ng can pronounce
"""

# Nepali Devanagari to Latin transliteration mapping
NEPALI_TO_LATIN = {
    # Vowels
    'अ': 'a',
    'आ': 'aa',
    'इ': 'i', 
    'ई': 'ii',
    'उ': 'u',
    'ऊ': 'uu',
    'ऋ': 'ri',
    'ए': 'e',
    'ऐ': 'ai',
    'ओ': 'o',
    'औ': 'au',
    
    # Consonants
    'क': 'ka',
    'ख': 'kha',
    'ग': 'ga',
    'घ': 'gha',
    'ङ': 'nga',
    'च': 'cha',
    'छ': 'chha',
    'ज': 'ja',
    'झ': 'jha',
    'ञ': 'nya',
    'ट': 'ta',
    'ठ': 'tha',
    'ड': 'da',
    'ढ': 'dha',
    'ण': 'na',
    'त': 'ta',
    'थ': 'tha',
    'द': 'da',
    'ध': 'dha',
    'न': 'na',
    'प': 'pa',
    'फ': 'pha',
    'ब': 'ba',
    'भ': 'bha',
    'म': 'ma',
    'य': 'ya',
    'र': 'ra',
    'ल': 'la',
    'व': 'wa',
    'श': 'sha',
    'ष': 'sha',
    'स': 'sa',
    'ह': 'ha',
    
    # Vowel diacritics (matras)
    'ा': 'aa',
    'ि': 'i',
    'ी': 'ii',
    'ु': 'u',
    'ू': 'uu',
    'ृ': 'ri',
    'े': 'e',
    'ै': 'ai',
    'ो': 'o',
    'ौ': 'au',
    
    # Special characters
    'ँ': 'n',  # Chandrabindu
    'ं': 'n',  # Anusvara
    'ः': 'h',  # Visarga
    '्': '',   # Halant (virama) - sign of no vowel
    '।': '.',  # Danda (period)
    '॥': '..',  # Double danda
    'ऽ': '',   # Avagraha
}

def transliterate_nepali_to_latin(text: str) -> str:
    """
    Convert Nepali Devanagari script to Latin characters for TTS.
    Preserves English text and other characters unchanged.
    """
    if not text:
        return text
    
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        
        # Check if it's a Nepali character
        if char in NEPALI_TO_LATIN:
            latin = NEPALI_TO_LATIN[char]
            # Check if next character is a vowel diacritical mark and handle it
            if i + 1 < len(text) and text[i + 1] in ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'े', 'ै', 'ो', 'ौ']:
                # Vowel mark follows consonant
                next_char = text[i + 1]
                next_latin = NEPALI_TO_LATIN[next_char]
                
                # Remove default 'a' from consonant if vowel mark is present
                if latin.endswith('a') and next_latin:
                    latin = latin[:-1]
                elif latin.endswith('a') and not next_latin:
                    latin = latin[:-1]
                
                result.append(latin + next_latin)
                i += 2
                continue
            
            result.append(latin)
        else:
            # Keep English text, spaces, punctuation as-is
            result.append(char)
        
        i += 1
    
    output = ''.join(result)
    # Clean up multiple spaces
    import re
    output = re.sub(r'\s+', ' ', output)
    return output.strip()


def is_nepali_text(text: str) -> bool:
    """Check if text contains Nepali Devanagari characters"""
    return any('\u0900' <= char <= '\u097f' for char in text)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "नमस्ते",  # Namaste
        "नमस्ते! म तपाईंको सहायक हुँ।",  # Namaste! I am your assistant.
        "तपाईंको नाम के हो",  # What is your name?
        "समय के हो",  # What time is it?
    ]
    
    for nepali_text in test_cases:
        latin_text = transliterate_nepali_to_latin(nepali_text)
        print(f"Nepali:  {nepali_text}")
        print(f"Latin:   {latin_text}")
        print()
