from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, date
from collections import Counter, defaultdict

@dataclass
class ChatMetadata:
    chat_id: int
    name: str
    chat_type: str 

@dataclass
class ContentAttributes:
    media_type_key: Optional[str] = None
    has_poll: bool = False
    has_forward: bool = False
    has_reply: bool = False
    is_paid: bool = False
    link_count: int = 0
    
    photos: int = 0
    videos: int = 0
    voice_messages: int = 0
    video_messages: int = 0
    stickers: int = 0
    gifs: int = 0
    files: int = 0
    audio: int = 0
    stories: int = 0
    paid_media: int = 0
    links: int = 0

@dataclass
class MessageStats:
    total_messages: int = 0
    total_symbols: int = 0
    non_consecutive_messages: int = 0
    non_consecutive_symbols: int = 0
    
                              
    reactions_received: int = 0
    
                   
    photos: int = 0
    videos: int = 0
    voice_messages: int = 0
    video_messages: int = 0
    stickers: int = 0
    gifs: int = 0
    files: int = 0
    links: int = 0
    audio: int = 0
    polls: int = 0
    
                     
    stories: int = 0
    paid_media: int = 0
    topic_messages: int = 0
    
                  
    forwards: int = 0
    replies: int = 0
    profanity: int = 0
    commands: int = 0
    
            
    pins: int = 0
    boosts: int = 0
    
    avg_len: float = 0.0
    
    def calculate_averages(self):
        if self.total_messages > 0:
            self.avg_len = self.total_symbols / self.total_messages

@dataclass
class UserActivity:
    first_msg_date: Optional[datetime] = None
    last_msg_date: Optional[datetime] = None
    first_msg_text: str = ""
    last_msg_text: str = ""
    active_days: set = field(default_factory=set)
    conversations_started: int = 0
    conversations_closed: int = 0
    
                  
    is_left: bool = False

@dataclass
class AnalysisResult:
    metadata: Optional[ChatMetadata] = None
    
    global_stats: MessageStats = field(default_factory=MessageStats)
    
    first_date: Optional[datetime] = None
    last_date: Optional[datetime] = None
    
    users_stats: Dict[str, MessageStats] = field(default_factory=lambda: defaultdict(MessageStats))
    users_activity: Dict[str, UserActivity] = field(default_factory=lambda: defaultdict(UserActivity))
    user_id_map: Dict[str, str] = field(default_factory=dict)

              
    top_words: List[tuple] = field(default_factory=list)
    top_phrases: List[tuple] = field(default_factory=list)      
    top_trigrams: List[tuple] = field(default_factory=list)     
    
    hours_activity: Counter = field(default_factory=Counter)
    weekdays_activity: Counter = field(default_factory=Counter)
    days_activity: Counter = field(default_factory=Counter)
    months_activity: Counter = field(default_factory=Counter)
    years_activity: Counter = field(default_factory=Counter)
    
                      
    daily_user_activity: Dict[date, Counter] = field(default_factory=lambda: defaultdict(Counter))
    daily_reactions: Counter = field(default_factory=Counter)
    
                                                        
    daily_symbol_count: Counter = field(default_factory=Counter)

                                                                            
    top_reacted_messages: List[Tuple[int, int, str]] = field(default_factory=list)
    
    top_reactions: List[tuple] = field(default_factory=list)
    top_posts: List[tuple] = field(default_factory=list)

    reading_time_seconds: int = 0

                   
    active_core_count: int = 0
    active_core_pct: float = 0.0
    
                  
    invites_stats: Counter = field(default_factory=lambda: Counter())
    creator_name: Optional[str] = None
    creator_id: Optional[str] = None

                      
    authors_monthly_activity: Dict[int, Counter] = field(default_factory=lambda: defaultdict(Counter))
    avg_reactions_per_post: float = 0.0
    content_distribution: Dict[str, int] = field(default_factory=dict)
    
                           
    heatmap_data: Counter = field(default_factory=Counter)
    daily_first_senders: Dict[Any, str] = field(default_factory=dict)
    avg_response_times: Dict[str, float] = field(default_factory=dict)
    
            
    errors: List[str] = field(default_factory=list)

    def get_duration_days(self) -> int:
        if self.first_date and self.last_date:
            return (self.last_date - self.first_date).days + 1
        return 0