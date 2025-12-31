from .base import BaseReporter
from core.i18n import t
import config
from datetime import datetime

class GroupReporter(BaseReporter):
    
    def _calc_duration(self, d1: datetime, d2: datetime) -> str:
        if not d1 or not d2: return ""
        diff = d2 - d1
        days = diff.days
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        
        parts = []
        if years > 0: parts.append(f"{years}{t('time-years-short')}")
        if months > 0: parts.append(f"{months}{t('time-months-short')}")
        if not parts: parts.append(f"0{t('time-months-short')}")
        
        return " ".join(parts)

    def render(self) -> str:
        self._render_header("💬")
        self._render_creator_info()

                    
        self._line(f"{self._e('messages')} {t('rep-total-messages')}: {self._fmt_num(self.data.global_stats.total_messages)}")
        self._line(f"{self._e('participant')} {t('rep-total-authors')}: {self._fmt_num(len(self.data.users_stats))}")
        
        active_days = len(self.data.days_activity)
        total_duration_days = self.data.get_duration_days()
        
        if total_duration_days > 0:
            perc = (active_days / total_duration_days) * 100
            self._line(f"{self._e('active_days')} {t('rep-active-days')}: {active_days} ({perc:.0f}%)")
        self._line()

                  
        self._render_media_block(self.data.global_stats)

                        
        if self.data.active_core_count > 0:
            self._line(f"🔥 {t('rep-core-desc', count=self.data.active_core_count)}")
            self._line(f"   ({self.data.active_core_pct:.1f}% {t('rep-from-all')})")
            self._line()

                   
        self._line(f"ℹ️ {t('legend-title')}")
        self._line()

                         
        sorted_names = self._get_sorted_participants()
        limit = config.TOP_PARTICIPANTS_LIMIT or len(sorted_names)
        
        for idx, name in enumerate(sorted_names[:limit], 1):
            u_stat = self.data.users_stats[name]
            u_act = self.data.users_activity[name]
            
                      
            perc_msgs = (u_stat.total_messages / (self.data.global_stats.total_messages or 1)) * 100
            
                                 
            days_active_count = len(u_act.active_days)
            perc_days = 0
            if total_duration_days > 0:
                perc_days = (days_active_count / total_duration_days) * 100

                      
            avg_sym = u_stat.avg_len
            avg_react = 0.0
            if u_stat.total_messages > 0:
                avg_react = u_stat.reactions_received / u_stat.total_messages

                         
            name_suffix = " 🚪" if u_act.is_left else ""
            
                    
            d_start = u_act.first_msg_date
            d_end = u_act.last_msg_date
            dur_str = self._calc_duration(d_start, d_end)
            date_range = f"{self._fmt_date(d_start)} – {self._fmt_date(d_end)}"

            self._line(f"{idx}. {name}{name_suffix}")
            
            self._line(f"   ├─ {self._e('messages')} {self._fmt_num(u_stat.total_messages)} ({perc_msgs:.1f}%)")
            self._line(f"   ├─ {self._e('symbols')} {self._fmt_num(u_stat.total_symbols)} ({t('avg-short')} {avg_sym:.0f})")
            self._line(f"   ├─ {self._e('reaction')} {self._fmt_num(u_stat.reactions_received)} ({t('avg-short')} {avg_react:.1f})")
            self._line(f"   ├─ {self._e('active_days')} {days_active_count} ({perc_days:.0f}%)")
            self._line(f"   └─ ⏱ {date_range} ({dur_str})")
            
            self._line()

                                 
        if self.data.top_reacted_messages:
            self._line(f"🏆 {t('top-reactions-msgs')}")
            for idx, (count, msg_id, author) in enumerate(self.data.top_reacted_messages, 1):
                link = self._get_msg_link(msg_id)
                self._line(f"   {idx}. {author}: {self._fmt_num(count)} {self._e('reaction')} {link}")
            self._line()

                  
        self._render_word_stats()

                     
        if self.data.invites_stats:
            self._line(f"🤝 {t('rep-top-inviters')}")
            top_inv = self.data.invites_stats.most_common(5)
            for idx, (name, count) in enumerate(top_inv, 1):
                self._line(f"   {idx}. {name}: {count}")
            self._line()

                                           
        self._render_time_patterns()
        
                                 
        self._render_top_days()
        
                    
        self._render_footer()

        return "\n".join(self.buffer)