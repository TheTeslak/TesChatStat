import os

INPUT_FILE = 'result.json'
OUTPUT_FILENAME_PATTERN = 'report'

                           
ANALYSIS_LANGUAGE = 'ru'
TIME_OFFSET = 0
START_DATE = None                        
END_DATE = None                          

                       
                                                      
                                                                   
LEMMATIZE_WORDS = False 

                                                                                      
                                                   
STOP_WORDS_TYPE = 'extended'

                                                                                      
                                                                     
MERGE_ENGLISH_STOPWORDS = True

                                       
STOPWORDS_FILENAME_RU_MINIMAL = 'stopwords.ru.minimal.txt'
STOPWORDS_FILENAME_RU_EXTENDED = 'stopwords.ru.extended.txt'
STOPWORDS_FILENAME_EN = 'stopwords.en.txt'
PROFANITY_FILENAME = 'profanity.all.txt'

TOP_WORDS_COUNT = 100
TOP_PHRASES_COUNT = 100

EXCLUDE_BOTS = True
BOT_IDENTIFIERS = ['bot', 'robot', 'служебный', 'assistant']
COMMAND_PREFIXES = ['/']

                             
NEW_DIALOG_THRESHOLD_HOURS = 1
EDITORIAL_HISTORY_LIMIT = 24                                   

SHOW_AUTHOR_LINKS = True
SHOW_USER_LINKS = False
PARTICIPANT_SORT_BY = 'messages'
TOP_PARTICIPANTS_LIMIT = 50 
TOP_DAYS_COUNT = 10

GENERATE_WORDCLOUD = True

EMOJIS = {
    'title': '💬',
    'channel_title': '📢',
    'participant': '👥',
    'word': '🔤',
    'phrase': '📝',
    'activity': '📊',
    'list_item': '➡️',
    'messages': '✉️',
    'symbols': '🔣',
    'avg_symbols': '💬',
    'active_days': '📅',
    'voice_message': '🎧',
    'video_message': '⏺',
    'forwarded': '↪️',
    'reply': '↩️',
    'pictures': '📷',
    'videos': '🎥',
    'gif': '🎬',
    'audios': '🎵',
    'files': '📑',
    'sticker': '💟',
    'command': '❗',
    'emoji': '😊',
    'profanity': '💢',
    'links': '🔗',
    'poll': '📊',
    'reading_time': '⏱',
    'reaction': '🔥',
    'bot': '🤖',
    'links_footer': '⚡️',
    'story': '🍩',
    'paid_media': '⭐️',
    'boost': '🚀',
    'topic': '📂',
    'pin': '📌'
}

FULL_JSON_EXPORT = False

               
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORDS_DIR = os.path.join(BASE_DIR, 'assets', 'stopwords')
LOCALES_DIR = os.path.join(BASE_DIR, 'assets', 'locales')
FONTS_DIR = os.path.join(BASE_DIR, 'assets', 'fonts')

REPORTS_DIR_NAME = '00 REPORTS'

TEXT_FONT_PATH = os.path.join(FONTS_DIR, 'Roboto.ttf')
EMOJI_FONT_PATH = os.path.join(FONTS_DIR, 'NotoColorEmoji.ttf')
WORDCLOUD_FONT_PATH = TEXT_FONT_PATH