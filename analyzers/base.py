from datetime import datetime, timedelta
from collections import Counter
from typing import Optional, Set, Union
import heapq
from core.types import AnalysisResult, MessageStats, ContentAttributes
from core.normalizer import extract_words, clean_text, URL_PATTERN
from core.i18n import t
import config

try:
    import pymorphy3
except ImportError:
    pymorphy3 = None

class BaseAnalyzer:
    def __init__(self, stop_words=None, profanity_words=None, start_date=None, end_date=None):
        self.result = AnalysisResult()
        
                      
        self.stop_words = set(stop_words or [])
        self.profanity_words = set(profanity_words or [])
        
        self.start_date = start_date
        self.end_date = end_date
        
        self.words_counter = Counter()
        self.phrases_counter = Counter()
        self.trigrams_counter = Counter()
        
        self.prev_user = None
        self.prev_time = None
        self.processed_ids: Set[Union[int, str]] = set()
        
        self.morph = None
        if config.LEMMATIZE_WORDS and pymorphy3:
            try:
                self.morph = pymorphy3.MorphAnalyzer()
            except Exception:
                pass

    def _is_bot(self, user_name: str) -> bool:
        if not config.EXCLUDE_BOTS:
            return False
        return any(bot_id in user_name.lower() for bot_id in config.BOT_IDENTIFIERS)

    def process_message(self, msg: dict) -> bool:
        try:
            if not self._check_id_integrity(msg):
                return False

            dt = self._parse_date(msg.get('date'), msg.get('date_unixtime'))
            if not dt: return False
            
            if self.start_date and dt < self.start_date: return False
            if self.end_date and dt > self.end_date: return False

            user = self._get_user(msg)
            msg_type = msg.get('type', 'message')
            
            if 'message_thread_id' in msg:
                self.result.global_stats.topic_messages += 1

            if msg_type == 'service':
                self._handle_service_event(msg, user)
                return False

            text_content = self._extract_text(msg)
            length = len(text_content)

            self.result.global_stats.total_messages += 1
            self.result.global_stats.total_symbols += length
            self.result.daily_symbol_count[dt.date()] += length
            self._update_time_stats(dt)

            if self._is_bot(user):
                self.prev_user = user 
                return True

            u_stat = self.result.users_stats[user]
            u_act = self.result.users_activity[user]
            
            if u_act.is_left: u_act.is_left = False

            u_stat.total_messages += 1
            u_stat.total_symbols += length
            self.result.daily_user_activity[dt.date()][user] += 1

            if self.prev_user != user:
                u_stat.non_consecutive_messages += 1
                u_stat.non_consecutive_symbols += length
                self.result.global_stats.non_consecutive_messages += 1
                self.result.global_stats.non_consecutive_symbols += length

            self._process_nlp(text_content, u_stat)
            
            content_attrs = self._extract_content_attributes(msg, text_content)
            self._apply_attributes(u_stat, content_attrs)
            self._apply_attributes(self.result.global_stats, content_attrs)
            
            self._count_reactions(msg, dt, user)
            self._update_timeline(u_act, dt, text_content)
            
            self.prev_user = user
            self.prev_time = dt
            return True

        except Exception as e:
            self.result.errors.append(t('err-msg-generic', id=msg.get('id', '?'), error=str(e)))
            return False

    def _process_nlp(self, text: str, u_stat: MessageStats):
        """
        Optimized NLP pipeline:
        1. Fast stopword check (raw word).
        2. Morphological analysis (expensive).
        3. Profanity & Final stopword check (normalized).
        """
        if not text: return

        if text.strip().startswith(tuple(config.COMMAND_PREFIXES)):
            self.result.global_stats.commands += 1
            u_stat.commands += 1

        cleaned = clean_text(text)
        raw_tokens = extract_words(cleaned)
        processed_tokens = []
        
        for word in raw_tokens:
                                                                                       
            if word in self.stop_words:
                continue

            normalized = word
            
                                                   
            if self.morph and not word.isascii():
                try:
                    normalized = self.morph.parse(word)[0].normal_form
                except Exception:
                    pass
            
                                                                                     
            is_profane = normalized in self.profanity_words
            if is_profane:
                self.result.global_stats.profanity += 1
                u_stat.profanity += 1

                                                                           
                                                                                              
            if is_profane or normalized in self.stop_words or len(normalized) < 2:
                continue
            
            processed_tokens.append(normalized)
        
        self.words_counter.update(processed_tokens)
        if len(processed_tokens) > 1:
            self.phrases_counter.update(f"{processed_tokens[i]} {processed_tokens[i+1]}" 
                                       for i in range(len(processed_tokens)-1))
        if len(processed_tokens) > 2:
            self.trigrams_counter.update(f"{processed_tokens[i]} {processed_tokens[i+1]} {processed_tokens[i+2]}" 
                                        for i in range(len(processed_tokens)-2))

    def _check_id_integrity(self, msg: dict) -> bool:
        msg_id = msg.get('id')
        if not msg_id: return True
        norm_id = int(msg_id) if str(msg_id).isdigit() else str(msg_id)
        if norm_id in self.processed_ids: return False
        self.processed_ids.add(norm_id)
        return True

    def _handle_service_event(self, msg: dict, user: str):
        action = msg.get('action')
        match action:
            case 'invite_members': self.result.invites_stats[user] += 1
            case 'pin_message': self.result.global_stats.pins += 1
            case 'boost_apply': self.result.global_stats.boosts += 1
            case 'create_group' | 'channel_created' | 'create_topic': self._process_creator(msg)
            case 'left_chat_member':
                if user: self.result.users_activity[user].is_left = True

    def _classify_media_type(self, msg: dict) -> str:
        if 'media_type' in msg: return msg['media_type']
                                                      
        if 'photo' in msg: return 'photo'
        if 'file' in msg: return 'file'
        if 'poll' in msg: return 'poll'
        if 'sticker' in msg: return 'sticker'
        if 'location' in msg: return 'location'
        if 'contact' in msg: return 'contact'
        if 'forwarded_from' in msg: return 'forward'
        return 'text'

    def _extract_content_attributes(self, msg: dict, text_content: str) -> ContentAttributes:
        attrs = ContentAttributes()
        m_type = msg.get('media_type', '')
        
        match m_type:
            case 'voice_message': attrs.voice_messages = 1
            case 'video_message': attrs.video_messages = 1
            case 'sticker': attrs.stickers = 1
            case 'animation': attrs.gifs = 1
            case 'audio_file': attrs.audio = 1
            case 'story': attrs.stories = 1
            case 'video_file':
                name = str(msg.get('file', '')).lower()
                attrs.gifs = 1 if 'gif' in name or 'gif' in str(msg.get('mime_type', '')) else 0
                attrs.videos = 1 if attrs.gifs == 0 else 0
            case 'photo': attrs.photos = 1
            case _:
                if 'photo' in msg: attrs.photos = 1
                elif 'file' in msg or m_type == 'document': attrs.files = 1

        attrs.has_poll = 'poll' in msg
        attrs.has_forward = 'forwarded_from' in msg
        attrs.has_reply = 'reply_to_message_id' in msg
        attrs.is_paid = bool(msg.get('is_paid_media') or msg.get('paid_media_data'))
            
                                                                                  
        unique_links = set()
        
                          
        entities = msg.get('text_entities', [])
        if isinstance(msg.get('text'), list):
            entities.extend([p for p in msg['text'] if isinstance(p, dict)])

        for e in entities:
            if e.get('type') in ('text_link', 'url'):
                val = e.get('href') or e.get('text')
                if val: unique_links.add(val.lower().rstrip('/'))
        
                                                                     
        if not unique_links:
             raw_links = URL_PATTERN.findall(text_content)
             for link in raw_links: unique_links.add(link.lower().rstrip('/'))
                
        attrs.link_count = len(unique_links)
        return attrs

    def _apply_attributes(self, stat: MessageStats, attrs: ContentAttributes):
        stat.photos += attrs.photos
        stat.videos += attrs.videos
        stat.voice_messages += attrs.voice_messages
        stat.video_messages += attrs.video_messages
        stat.stickers += attrs.stickers
        stat.gifs += attrs.gifs
        stat.files += attrs.files
        stat.audio += attrs.audio
        stat.stories += attrs.stories
        stat.paid_media += attrs.paid_media if attrs.is_paid else 0
        stat.polls += 1 if attrs.has_poll else 0
        stat.forwards += 1 if attrs.has_forward else 0
        stat.replies += 1 if attrs.has_reply else 0
        stat.links += attrs.link_count

    def _count_reactions(self, msg: dict, dt: datetime, author: str):
        reactions = msg.get('reactions', [])
        if reactions:
            total = sum(r.get('count', 0) for r in reactions)
            if total > 0:
                self.result.daily_reactions[dt.date()] += total
                if author and not self._is_bot(author):
                    self.result.users_stats[author].reactions_received += total
                
                mid = msg.get('id', 0)
                heap = self.result.top_reacted_messages
                if len(heap) < 10: heapq.heappush(heap, (total, mid, author))
                elif total > heap[0][0]: heapq.heapreplace(heap, (total, mid, author))

    def finalize(self):
        self.result.top_words = self.words_counter.most_common(config.TOP_WORDS_COUNT)
        self.result.top_phrases = self.phrases_counter.most_common(config.TOP_PHRASES_COUNT)
        self.result.top_trigrams = self.trigrams_counter.most_common(config.TOP_PHRASES_COUNT)
        self.result.top_reacted_messages.sort(key=lambda x: x[0], reverse=True)

    def _process_creator(self, msg: dict):
        actor = msg.get('actor') or msg.get('from')
        if actor:
            self.result.creator_name = actor
            self.result.creator_id = self._extract_id(msg)

    def _update_timeline(self, u_act, dt, text):
        clean = text.replace('\n', ' ').strip()
        preview = (clean[:60] + "...") if len(clean) > 60 else clean
        if preview:
            if not u_act.first_msg_text: 
                u_act.first_msg_date, u_act.first_msg_text = dt, preview
            u_act.last_msg_date, u_act.last_msg_text = dt, preview
        u_act.active_days.add(dt.date())

    def _parse_date(self, d_iso, d_unix=None) -> Optional[datetime]:
        dt = None
        if d_iso and isinstance(d_iso, str):
            try: dt = datetime.fromisoformat(d_iso)
            except ValueError: pass
        if not dt and d_unix:
            try: dt = datetime.fromtimestamp(float(d_unix))
            except (ValueError, TypeError): pass
        if dt:
            dt = dt.replace(tzinfo=None)
            if config.TIME_OFFSET: dt += timedelta(hours=config.TIME_OFFSET)
            if not self.result.first_date or dt < self.result.first_date: self.result.first_date = dt
            if not self.result.last_date or dt > self.result.last_date: self.result.last_date = dt
        return dt

    def _extract_id(self, msg: dict) -> Optional[str]:
        raw = msg.get('from_id') or msg.get('actor_id')
        if not raw: return None
        s = str(raw)
        return s[4:] if s.startswith('user') else (s[7:] if s.startswith('channel') else s)

    def _get_user(self, msg: dict) -> str:
        name = msg.get('from') or msg.get('author') or msg.get('actor') or 'Unknown'
        uid = self._extract_id(msg)
        if uid: self.result.user_id_map[uid] = name
        return self.result.user_id_map.get(uid, name) if uid else name

    def _extract_text(self, msg: dict) -> str:
        val = msg.get('text', '')
        if not val: return ""
        if isinstance(val, str): return val
        return "".join(p if isinstance(p, str) else str(p.get('text', '')) for p in val) if isinstance(val, list) else str(val)

    def _update_time_stats(self, dt: datetime):
        self.result.hours_activity[dt.hour] += 1
        self.result.weekdays_activity[dt.weekday()] += 1
        self.result.days_activity[dt.date()] += 1
        self.result.months_activity[(dt.year, dt.month)] += 1
        self.result.years_activity[dt.year] += 1