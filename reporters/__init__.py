from core.types import ChatMetadata
from .base import BaseReporter
from .personal import PersonalReporter
from .group import GroupReporter
from .channel import ChannelReporter

def get_reporter(metadata: ChatMetadata, result) -> BaseReporter:
    t = metadata.chat_type
    
    if t == 'personal_chat':
        return PersonalReporter(result)
    elif 'channel' in t:
        return ChannelReporter(result)
    else:
        return GroupReporter(result)