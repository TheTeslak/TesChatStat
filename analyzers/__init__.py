from core.types import ChatMetadata
from .base import BaseAnalyzer
from .personal import PersonalAnalyzer
from .group import GroupAnalyzer
from .channel import ChannelAnalyzer

def get_analyzer(metadata: ChatMetadata, stop_words: set, profanity_words: set, start_date=None, end_date=None) -> BaseAnalyzer:
    """Factory method to select the correct analyzer strategy."""
    
    t = metadata.chat_type
    
                                                                    
    if t == 'personal_chat':
        return PersonalAnalyzer(stop_words, profanity_words, start_date=start_date, end_date=end_date)
    elif 'channel' in t:
        return ChannelAnalyzer(stop_words, profanity_words, start_date=start_date, end_date=end_date)
    else:
        return GroupAnalyzer(stop_words, profanity_words, start_date=start_date, end_date=end_date)