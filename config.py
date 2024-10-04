# -------------------------
# Settings
# -------------------------

input_file = 'result.json'  # Name of the main file for analysis

merge_folder = ''  # Folder containing JSON files for merging; leave as '' to use the current directory

# Output filename pattern
output_filename_pattern = '<chat_name>_<timestamp>.txt'  # Output report filename; <chat_name> will be replaced with chat name

# List of stop words to exclude from frequent words analysis
stop_words = ['и', 'в', 'не', 'на', 'с', 'что', 'а', 'как', 'это', 'по', 'но', 'из', 'у', 'за', 'о', 'же', 'то', 'к', 'для', 'до', 'вы', 'мы', 'они', 'он', 'она', 'оно', 'так', 'было', 'только', 'бы', 'когда', 'уже']

top_participants_count = None  # Set to None to display all participants
top_words_count = 100  # Number of top words to display

emojis = {
    'title': '💬',
    'participant': '👥',
    'word': '🔠',
    'activity': '📊',
    'list_item': '➡️',
    'messages': '✉️',
    'symbols': '🔣',
    'avg_symbols': '💬',
    'voice': '🎵',
    'forwarded': '📩',
    'pictures': '🖼',
    'videos': '📹',
    'gif': '🎬',
    'audios': '🎧',
    'files': '📑',
    'sticker': '💌',
    'command': '❗',
    'emoji': '🥵',
    'profanity': '💢',
    'links': '🔗',
    'poll': '📊',
}

top_days_count = 10  # Number of most active days to display

show_non_consecutive_counts = True  # Display messages non-consecutively in the report

exclude_bots = True  # Whether to exclude bots from analysis
bot_identifiers = ['Bot']  # Strings to identify bots

# Day names and month names in Russian and English
day_names = {
    'ru': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
}
month_names = {
    'ru': ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
}

# Words to detect profanity in messages
profanity_words = ['пиздец', 'слово2', 'слово3']  # Replace with real profane words

# Command prefixes (e.g., '/')
commands_identifiers = ['/']

# Regular expression to find emojis
import re
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # Emoticons
                           u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
                           u"\U0001F680-\U0001F6FF"  # Transport & Map
                           u"\U0001F1E0-\U0001F1FF"  # Flags
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251"  # Enclosed characters
                           "]+", flags=re.UNICODE)

# Regular expression to find URLs
url_pattern = re.compile(
    r'(?i)\b((?:https?:\/\/|www\d{0,3}[.]|telegram[.]me\/|t[.]me\/|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+)', re.IGNORECASE)

show_author_links = True  # Set to False to disable displaying my links. TG @Teslak & @TesNot

show_user_links = False  # False by default

# -------------------------
# End of Settings
# -------------------------