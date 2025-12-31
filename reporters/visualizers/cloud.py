import os
from typing import Optional
from wordcloud import WordCloud
from core.types import AnalysisResult
import config

def generate_word_cloud(result: AnalysisResult, output_dir: str) -> Optional[str]:
    """
    Generates a high-resolution Word Cloud.
    """
    if not config.GENERATE_WORDCLOUD:
        return None
        
    if not result.top_words:
        return "WordCloud skipped: No words found."

    freq_dict = {w: c for w, c in result.top_words if len(w) > 2}
    if not freq_dict:
        return "WordCloud skipped: Insufficient words."

    font_path = config.WORDCLOUD_FONT_PATH if os.path.exists(config.WORDCLOUD_FONT_PATH) else None

    try:
        wc = WordCloud(
            width=3200, 
            height=1600,
            background_color='white',
            font_path=font_path,
            max_words=250,
            collocations=False,
            prefer_horizontal=0.9,
            margin=10
        ).generate_from_frequencies(freq_dict)
        
        filename = os.path.join(output_dir, 'wordcloud.png')
        wc.to_file(filename)
        return None
    except Exception as e:
        return f"WordCloud Error: {str(e)}"