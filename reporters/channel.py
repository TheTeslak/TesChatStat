from .base import BaseReporter
from core.i18n import t
import config

class ChannelReporter(BaseReporter):
    def render(self) -> str:
        self._render_header("📢")
        self._render_creator_info()

                    
        self._line(t('channel-summary-title'))
        self._line(f"{self._e('messages')} {t('total-posts')}: {self._fmt_num(self.data.global_stats.total_messages)}")
        self._line(f"{self._e('avg_symbols')} {t('avg-post-len')}: {self.data.global_stats.avg_len:.0f}")
        self._line(f"{self._e('participant')} {t('total-authors')}: {len(self.data.users_stats)}")
        self._line()

                       
        self._line(t('engagement-title'))
        self._line(f"🔥 {t('avg-reactions')}: {self.data.avg_reactions_per_post:.2f}")
        
        if self.data.top_reactions:
            self._line(f"{t('top-reactions-label')}:")
            parts = [f"{e} {c}" for e, c in self.data.top_reactions[:5]]
            self._line("   " + "  ".join(parts))
        self._line()

        if self.data.content_distribution:
            self._line(t('content-types-title'))
            sorted_types = sorted(self.data.content_distribution.items(), key=lambda x: x[1], reverse=True)
            for c_type, count in sorted_types:
                                                                                                        
                label = t(f'type-{c_type}', default=c_type.capitalize())
                self._line(f"   {label}: {self._fmt_num(count)}")
            self._line()

                      
        if self.data.top_posts:
            self._line(t('top-posts-title'))
                                                                 
            for idx, (mid, count) in enumerate(self.data.top_posts, 1):
                self._line(f"   {idx}. ID {mid}: {self._fmt_num(count)} {self._e('reaction')}")
            self._line()

                                                                      
        if self.data.authors_monthly_activity:
            self._line(t('editorial-title'))
            
            sorted_months = sorted(self.data.authors_monthly_activity.keys(), reverse=True)
            
            for key in sorted_months[:24]:
                year = key // 100
                month = key % 100
                
                m_name = t(f'month-{month}')
                if m_name.startswith('month-'): m_name = str(month)
                
                self._line(f"📅 {m_name} {year}")
                
                month_stats = self.data.authors_monthly_activity[key]
                for author, count in month_stats.most_common(5):
                    self._line(f"   └─ {author}: {self._fmt_num(count)}")
                self._line()

        self._render_word_stats()
        self._render_media_block(self.data.global_stats, "media-title")
        self._render_footer()

        return "\n".join(self.buffer)