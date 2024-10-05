# -------------------------
# Settings
# -------------------------

input_file = 'result.json'  # Name of the main file for analysis

merge_folder = ''  # Folder containing JSON files for merging; leave as '' to use the current directory

# Output filename pattern
output_filename_pattern = '<chat_name>_<timestamp>.txt'  # Output report filename; <chat_name> will be replaced with chat name

# List of stop words to exclude from frequent words analysis
stop_words_type = 'minimal'  # 'minimal' or 'extended'

top_participants_count = None  # Set to None to display all participants
top_words_count = 100  # Number of top words to display
top_phrases_count = 100  # Number of top phrases to display

emojis = {
    'title': '💬',
    'participant': '👥',
    'word': '🔠',
    'phrase': '📝',
    'activity': '📊',
    'list_item': '➡️',
    'messages': '✉️',
    'symbols': '🔣',
    'avg_symbols': '💬',
    'voice': '🎵',
    'forwarded': '📩',
    'pictures': '🖼',
    'videos': '🎥',
    'gif': '🎬',
    'audios': '🎧',
    'files': '📑',
    'sticker': '💌',
    'command': '❗',
    'emoji': '😊',
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

show_author_links = True  # Set to False to disable displaying author links

show_user_links = False  # False by default

first_message_interval_hours = 1  # Default interval in hours to consider who wrote first

words_dir = 'words'  # Directory where stop words and profanity lists are stored

time_offset = 0  # Time offset in hours to adjust message timestamps

plot_non_consecutive_messages = False  # Default behavior is to plot based on total messages

# -------------------------
# End of Settings
# -------------------------