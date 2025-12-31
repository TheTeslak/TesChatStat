from .base import BaseReporter
from core.i18n import t
import config

class PersonalReporter(BaseReporter):
    def render(self) -> str:
        self._render_header("💬")
        
                    
        self._line(t('rep-summary-title'))
        self._line(f"{self._e('messages')} {t('rep-total-messages')}: {self._fmt_num(self.data.global_stats.total_messages)}")
        self._line(f"{self._e('symbols')} {t('rep-total-symbols')}: {self._fmt_num(self.data.global_stats.total_symbols)}")
        
        seconds = self.data.reading_time_seconds
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        
                                   
        time_str = t('time-duration-fmt', days=days, hours=hours)
        if time_str.startswith('time-duration'):           
            time_str = f"{days}d {hours}h"
        
        self._line(f"{self._e('reading_time')} {t('rep-reading-time')}: {time_str}")
        self._line()

                         
        self._line(t('rep-participants'))
        
        users = sorted(self.data.users_stats.items(), key=lambda x: x[1].total_messages, reverse=True)
        
        if not users:
            self._line(t('rep-no-participants', default="No active participants."))
            return "\n".join(self.buffer)

        if len(users) >= 2:
            u1_name, u1_stat = users[0]
            u2_name, u2_stat = users[1]
            diff = u1_stat.total_messages - u2_stat.total_messages
            self._line(t('rep-winner-diff', name=u1_name, count=self._fmt_num(diff)))
            self._line()

        for name, stats in users:
            total = self.data.global_stats.total_messages or 1
            perc = (stats.total_messages / total) * 100
            activity = self.data.users_activity[name]

            self._line(f"{name}")
            self._line(f"   ├─ {self._e('messages')} {self._fmt_num(stats.total_messages)} ({perc:.0f}%)")
            
                           
            resp_time = self.data.avg_response_times.get(name)
            if resp_time:
                mins = int(resp_time // 60)
                self._line(f"   ├─ {self._e('reading_time', '⏱')} {t('rep-avg-response')}: {mins} {t('rep-min')}")
            
                               
            self._line(f"   ├─ {t('rep-started-closed', started=activity.conversations_started, closed=activity.conversations_closed)}")
            
                                                         
            if activity.first_msg_text:
                preview = self._clean(activity.first_msg_text)[:30]
                self._line(f"   ├─ {t('rep-timeline-first', text=preview)}")
            if activity.last_msg_text:
                preview = self._clean(activity.last_msg_text)[:30]
                self._line(f"   └─ {t('rep-timeline-last', text=preview)}")
            
            self._line()

        self._render_word_stats()
        self._render_media_block(self.data.global_stats, "media-title")
        self._render_top_days()
        self._render_footer()

        return "\n".join(self.buffer)