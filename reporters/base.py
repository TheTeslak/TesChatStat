from datetime import datetime
from core.types import AnalysisResult, MessageStats
from core.constants import GITHUB_REPO_URL, TELEGRAM_CHANNEL_URL
from core.i18n import t
import config

class BaseReporter:
    def __init__(self, result: AnalysisResult):
        self.data = result
        self.buffer = []

    def render(self) -> str:
        """Override this method in subclasses."""
        return ""

    def _line(self, text: str = ""):
        self.buffer.append(text)

    def _fmt_num(self, n: int) -> str:
        """Formats numbers with spaces (e.g. 1 000)."""
        return f"{n:,}".replace(",", " ")

    def _fmt_date(self, dt: datetime) -> str:
        if not dt: return "..."
        return dt.strftime("%d.%m.%Y")
    
    def _e(self, key, default='•'):
        """Safely retrieve emoji from config."""
        return config.EMOJIS.get(key, default)

    def _get_msg_link(self, msg_id) -> str:
        """Generates t.me/c/ link. Handles negative IDs."""
        cid = self.data.metadata.chat_id
        if not cid: return ""
        
        cid_str = str(cid)
                                          
        if cid_str.startswith("-100"):
            cid_str = cid_str[4:]
        elif cid_str.startswith("-"):
            cid_str = cid_str[1:]
            
        return f"https://t.me/c/{cid_str}/{msg_id}"

    def _get_sorted_participants(self):
        stats = self.data.users_stats
        activity = self.data.users_activity
        
                                        
        for s in stats.values():
            s.calculate_averages()
        
        def get_media_total(s: MessageStats) -> int:
            return (s.photos + s.videos + s.voice_messages + 
                    s.video_messages + s.stickers + s.gifs + 
                    s.files + s.audio + s.stories + s.paid_media)

        sort_map = {
            'messages': lambda x: stats[x].total_messages,
            'symbols': lambda x: stats[x].total_symbols,
            'avg_len': lambda x: stats[x].avg_len if stats[x].total_messages >= 10 else 0,
            'active_days': lambda x: len(activity[x].active_days),
            'media': lambda x: get_media_total(stats[x]),
            'reactions': lambda x: stats[x].reactions_received,
            'tenure': lambda x: (activity[x].last_msg_date - activity[x].first_msg_date).total_seconds() if activity[x].last_msg_date else 0,
            'alphabet': lambda x: x.lower()
        }
        
        sort_key = sort_map.get(config.PARTICIPANT_SORT_BY, sort_map['messages'])
        should_reverse = (config.PARTICIPANT_SORT_BY != 'alphabet')
        
        return sorted(stats.keys(), key=sort_key, reverse=should_reverse)

    def _render_header(self, emoji_icon: str, title_suffix: str = ""):
        name = self.data.metadata.name if self.data.metadata else "Unknown"
        self._line(f"{emoji_icon} {name} {title_suffix}")
        
        chat_type = self.data.metadata.chat_type if self.data.metadata else "unknown"
        chat_id = self.data.metadata.chat_id if self.data.metadata else "?"
        
        self._line(f"ID {chat_id} · {chat_type}")
            
        period = f"{self._fmt_date(self.data.first_date)} – {self._fmt_date(self.data.last_date)}"
        self._line(f"📅 {period}")
        self._line()

    def _render_creator_info(self):
        if self.data.creator_name:
            creator_str = f"👑 {t('meta-creator')}: {self.data.creator_name}"
            if self.data.creator_id:
                creator_str += f" (ID {self.data.creator_id})"
            self._line(creator_str)
            self._line()

    def _render_media_block(self, stats: MessageStats, title_key: str = None):
        """
        Renders media statistics.
        Args:
            stats: The MessageStats object.
            title_key: Optional translation key for the header (e.g., 'media-title').
        """
        if title_key:
            self._line(f"📁 {t(title_key)}")

        def add(emoji_key, count, label_key):
            if count > 0:
                self._line(f"{self._e(emoji_key)} {t(label_key)}: {self._fmt_num(count)}")

        add('forwarded', stats.forwards, 'media-forwards')
        add('reply', stats.replies, 'media-replies')
        add('pictures', stats.photos, 'media-pictures')
        add('videos', stats.videos, 'media-videos')
        add('voice_message', stats.voice_messages, 'media-voice')
        add('video_message', stats.video_messages, 'media-video-notes')
        add('sticker', stats.stickers, 'media-stickers')
        add('audios', stats.audio, 'media-audio')
        add('gif', stats.gifs, 'media-gif')
        add('files', stats.files, 'media-files')
        add('story', stats.stories, 'media-stories')
        add('paid_media', stats.paid_media, 'media-paid')
        add('links', stats.links, 'media-links')
        add('poll', stats.polls, 'media-polls')
        
        if stats is self.data.global_stats:
            add('boost', stats.boosts, 'media-boosts')
            add('pin', stats.pins, 'media-pins')
            if stats.topic_messages > 0:
                self._line(f"{self._e('topic')} {t('media-topics')}: {self._fmt_num(stats.topic_messages)}")
        
        if stats.profanity > 0:
            add('profanity', stats.profanity, 'media-profanity')
            
        self._line()

    def _render_word_stats(self):
        words = self.data.top_words[:15]
        phrases = self.data.top_phrases[:10]
        trigrams = getattr(self.data, 'top_trigrams', [])[:10]
        
        if not words: return

        self._line(f"{self._e('word')} {t('top-words-title')}")
        
        if words:
            self._line(f"├─ {t('words')}:")
            for i, (w, count) in enumerate(words, 1):
                self._line(f"│  {i}. {w} ({self._fmt_num(count)})")
        
        if phrases:
            self._line(f"│")
            self._line(f"├─ {t('phrases-2')}:")
            for i, (p, count) in enumerate(phrases, 1):
                self._line(f"│  {i}. {p} ({self._fmt_num(count)})")

        if trigrams:
            self._line(f"│")
            self._line(f"└─ {t('phrases-3')}:")
            for i, (t_gram, count) in enumerate(trigrams, 1):
                self._line(f"   {i}. {t_gram} ({self._fmt_num(count)})")
        
        self._line()

    def _render_time_patterns(self):
        self._line(f"📊 {t('time-patterns-title', default='Activity Peaks')}")
        
        def fmt_list(items):
            return "➡️ " + ", ➡️ ".join(items)

                  
        hours_top = [f"{h:02d}:00–{h:02d}:59" for h, _ in self.data.hours_activity.most_common(3)]
        if hours_top: self._line(fmt_list(hours_top))
        
                     
        days_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        days_top = [t(days_map[d], default=str(d)) for d, _ in self.data.weekdays_activity.most_common(3)]
        if days_top: self._line(fmt_list(days_top))

                   
        months_top = []
        for (y, m), _ in self.data.months_activity.most_common(3):
            m_name = t(f'month-{m}', default=str(m))
            months_top.append(f"{m_name} {y}")
        if months_top: self._line(fmt_list(months_top))
        
                  
        years_top = [str(y) for y, _ in self.data.years_activity.most_common(3)]
        if years_top: self._line(fmt_list(years_top))

        self._line()

    def _render_top_days(self):
        self._line(f"📊 {t('top-days-title', count=config.TOP_DAYS_COUNT)}")
        
        top = self.data.days_activity.most_common(config.TOP_DAYS_COUNT)
        for idx, (date_obj, count) in enumerate(top, 1):
            date_str = date_obj.strftime("%d.%m.%Y")
            
                                                           
            symbols = self.data.daily_symbol_count.get(date_obj, 0)
            avg_len = symbols / count if count > 0 else 0
            
            row = (f"{idx}. {date_str}: "
                   f"{self._e('messages')} {self._fmt_num(count)}, "
                   f"{self._e('symbols')} {self._fmt_num(symbols)}, "
                   f"{self._e('avg_symbols')} {avg_len:.1f}")
            self._line(row)
            
        self._line()

    def _render_footer(self):
        if config.SHOW_AUTHOR_LINKS:
            self._line("⚡️")
            self._line(f"⚡️ {t('footer-updates', default='GitHub Updates')}: {GITHUB_REPO_URL}")
            self._line(f"⚡️ {t('footer-channel', default='Telegram Channel')}: {TELEGRAM_CHANNEL_URL}")
            self._line("⚡️")