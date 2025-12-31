import os
import config
from datetime import datetime

def save_current_config():
    """
    Overwrites config.py with the current values in memory.
    Preserves structure and comments for readability.
    """
    try:
        content = [
            "import os",
            "",
            f"INPUT_FILE = {repr(config.INPUT_FILE)}",
            f"OUTPUT_FILENAME_PATTERN = {repr(config.OUTPUT_FILENAME_PATTERN)}",
            "",
            "# --- Analysis Settings ---",
            f"ANALYSIS_LANGUAGE = {repr(config.ANALYSIS_LANGUAGE)}",
            f"TIME_OFFSET = {repr(config.TIME_OFFSET)}",
            "START_DATE = None  # Format: 'DD.MM.YYYY'",
            "END_DATE = None    # Format: 'DD.MM.YYYY'",
            "",
            "# --- NLP & Filters ---",
            f"LEMMATIZE_WORDS = {repr(config.LEMMATIZE_WORDS)}",
            f"RU_STOP_WORDS_TYPE = {repr(config.RU_STOP_WORDS_TYPE)}",
            f"TOP_WORDS_COUNT = {repr(config.TOP_WORDS_COUNT)}",
            f"TOP_PHRASES_COUNT = {repr(config.TOP_PHRASES_COUNT)}",
            "",
            f"EXCLUDE_BOTS = {repr(config.EXCLUDE_BOTS)}",
            f"BOT_IDENTIFIERS = {repr(config.BOT_IDENTIFIERS)}",
            f"COMMAND_PREFIXES = {repr(config.COMMAND_PREFIXES)}",
            "",
            "# --- Thresholds ---",
            f"NEW_DIALOG_THRESHOLD_HOURS = {repr(config.NEW_DIALOG_THRESHOLD_HOURS)}",
            "",
            f"SHOW_AUTHOR_LINKS = {repr(config.SHOW_AUTHOR_LINKS)}",
            f"SHOW_USER_LINKS = {repr(config.SHOW_USER_LINKS)}",
            f"PARTICIPANT_SORT_BY = {repr(config.PARTICIPANT_SORT_BY)}",
            f"TOP_PARTICIPANTS_LIMIT = {repr(config.TOP_PARTICIPANTS_LIMIT)}",
            f"TOP_DAYS_COUNT = {repr(config.TOP_DAYS_COUNT)}",
            "",
            f"GENERATE_WORDCLOUD = {repr(config.GENERATE_WORDCLOUD)}",
            "",
            "# --- Export ---",
            f"FULL_JSON_EXPORT = {repr(config.FULL_JSON_EXPORT)}",
            "",
            "EMOJIS = {",
        ]
        
                             
        for k, v in config.EMOJIS.items():
            content.append(f"    {repr(k)}: {repr(v)},")
        content.append("}")
        
                      
        content.extend([
            "",
            "BASE_DIR = os.path.dirname(os.path.abspath(__file__))",
            "WORDS_DIR = os.path.join(BASE_DIR, 'assets', 'stopwords')",
            "LOCALES_DIR = os.path.join(BASE_DIR, 'assets', 'locales')",
            "FONTS_DIR = os.path.join(BASE_DIR, 'assets', 'fonts')",
            "",
            f"REPORTS_DIR_NAME = {repr(config.REPORTS_DIR_NAME)}",
            "",
            "TEXT_FONT_PATH = os.path.join(FONTS_DIR, 'Roboto.ttf')",
            "EMOJI_FONT_PATH = os.path.join(FONTS_DIR, 'NotoColorEmoji.ttf')",
            "WORDCLOUD_FONT_PATH = TEXT_FONT_PATH"
        ])

        with open('config.py', 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
            
        return True, None
    except Exception as e:
        return False, str(e)