from collections import Counter
from .base import BaseAnalyzer

class ChannelAnalyzer(BaseAnalyzer):
    def __init__(self, stop_words=None, profanity_words=None, start_date=None, end_date=None):
        super().__init__(stop_words, profanity_words, start_date=start_date, end_date=end_date)
        
        self.reactions_counter = Counter()
        self.posts_reactions = [] 
        self.total_reactions = 0
        self.content_types = Counter()

    def process_message(self, msg: dict) -> bool:
                                                      
        is_processed = super().process_message(msg)
        
        if is_processed:
                                                
            dt = self.prev_time
            user = self.prev_user
            
            if dt and user:
                key = dt.year * 100 + dt.month
                self.result.authors_monthly_activity[key][user] += 1
            
                                                      
            c_type = self._classify_media_type(msg)
            self.content_types[c_type] += 1

                                       
            reactions = msg.get('reactions', [])
            if reactions:
                msg_total_reactions = 0
                for r in reactions:
                    emoji = r.get('emoji')
                    count = r.get('count', 0)
                    if emoji:
                        self.reactions_counter[emoji] += count
                    msg_total_reactions += count
                
                self.total_reactions += msg_total_reactions
                
                if msg_total_reactions > 0:
                    self.posts_reactions.append((msg.get('id'), msg_total_reactions))
        
        return is_processed

    def finalize(self):
        super().finalize()
        
        self.result.top_reactions = self.reactions_counter.most_common(10)
        
                                     
        valid_posts = [p for p in self.posts_reactions if p[1] >= 2]
        
                                  
        self.result.top_posts = sorted(
            valid_posts, 
            key=lambda x: x[1], 
            reverse=True
        )[:20]
        
        total_posts = self.result.global_stats.total_messages
        if total_posts > 0:
            self.result.avg_reactions_per_post = self.total_reactions / total_posts
            
        self.result.content_distribution = dict(self.content_types)