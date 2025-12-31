import os
import re
from typing import Set

                             
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
EMOJI_PATTERN = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
WORD_PATTERN = re.compile(r'\b[а-яА-Яa-zA-Z]+\b')

def load_word_list(filepath: str) -> Set[str]:
    """
    Generic loader for word lists (stopwords, profanity).
    
    Features:
    - Returns a Set for O(1) lookups.
    - Handles comments: ignores text after '#' on any line.
    - safe UTF-8 encoding.
    - Automatic lowercase and whitespace stripping.
    """
    if not os.path.exists(filepath):
        return set()
        
    words = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                                                        
                clean_line = line.split('#')[0]
                              
                token = clean_line.strip().lower()
                                      
                if token:
                    words.add(token)
    except OSError as e:
        print(f"⚠️ Warning: Failed to load dictionary '{os.path.basename(filepath)}': {e}")
        return set()
        
    return words

def clean_text(text: str) -> str:
    """Removes URLs and Emojis."""
    text = URL_PATTERN.sub('', text)
    text = EMOJI_PATTERN.sub('', text)
    return text.strip()

def extract_words(text: str) -> list[str]:
    return WORD_PATTERN.findall(text.lower())