from .base import BaseAnalyzer
from core.i18n import t
import config
from collections import defaultdict

class PersonalAnalyzer(BaseAnalyzer):
    def __init__(self, stop_words, profanity_words, start_date=None, end_date=None):
        super().__init__(stop_words, profanity_words, start_date=start_date, end_date=end_date)
        self.daily_first_senders = {} 
        self.response_times = defaultdict(list) 
        self.last_msg_time = None
        self.last_user = None

    def process_message(self, msg: dict) -> bool:
                                                                          
                                                                                                    
        
                                                 
        dt = self._parse_date(msg.get('date'), msg.get('date_unixtime'))
        if not dt: 
            return False
        
                                       
        if self.start_date and dt < self.start_date: return False
        if self.end_date and dt > self.end_date: return False
        
        user = self._get_user(msg)
        if self._is_bot(user): 
                                                                                
            return super().process_message(msg)

                                                      
        
                                                  
        if self.prev_time:
            delta_hours = (dt - self.prev_time).total_seconds() / 3600
            if delta_hours > config.NEW_DIALOG_THRESHOLD_HOURS:
                self.result.users_activity[user].conversations_started += 1
                if self.prev_user:
                    self.result.users_activity[self.prev_user].conversations_closed += 1

                             
        if self.last_msg_time and self.last_user:
            if user != self.last_user:
                diff = (dt - self.last_msg_time).total_seconds()
                                                               
                if diff < 8 * 3600:
                    self.response_times[user].append(diff)
        
                               
        self.last_msg_time = dt
        self.last_user = user
        
                            
        date_key = dt.date()
        if date_key not in self.daily_first_senders:
            self.daily_first_senders[date_key] = user

                                                                      
        return super().process_message(msg)

    def finalize(self):
        super().finalize()
        self.result.daily_first_senders = self.daily_first_senders
        
        for user, times in self.response_times.items():
            if times:
                self.result.avg_response_times[user] = sum(times) / len(times)
        
                                  
        total_chars = self.result.global_stats.total_symbols
        media_penalty = (
            self.result.global_stats.photos * 5 + 
            self.result.global_stats.videos * 30 +
            self.result.global_stats.voice_messages * 15
        )
        self.result.reading_time_seconds = int((total_chars / 15) + media_penalty)