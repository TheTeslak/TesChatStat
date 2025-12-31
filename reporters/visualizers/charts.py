import os
import re
import warnings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
from typing import List, Set
from datetime import date
from core.types import AnalysisResult
from core.i18n import t
import config

                                                                    
FIG_SIZE_INCHES = (12.8, 7.2)
CHART_DPI = 200

                                                         
EMOJI_REGEX = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)

def _sanitize_title(text: str) -> str:
    return EMOJI_REGEX.sub('', text).strip()

def generate_activity_chart(result: AnalysisResult, output_dir: str) -> List[str]:
    """Generates high-res activity charts per year."""
    errors = []
    
    if not result.metadata:
        return ["Metadata missing."]

    chat_type = result.metadata.chat_type
    
    all_dates: Set[date] = set(result.days_activity.keys())
    if 'channel' in chat_type:
        all_dates.update(result.daily_reactions.keys())
        
    if not all_dates:
        return []

    sorted_dates = sorted(list(all_dates))
    years = sorted(list({d.year for d in sorted_dates}))
    
                                                            
    global_max_msg = max(result.days_activity.values()) if result.days_activity else 0
    global_max_react = max(result.daily_reactions.values()) if 'channel' in chat_type and result.daily_reactions else 0

    y_limit_msg = global_max_msg * 1.1 if global_max_msg > 0 else 10
    y_limit_react = global_max_react * 1.1 if global_max_react > 0 else 10

                                    
    text_font = None
    if os.path.exists(config.TEXT_FONT_PATH):
        text_font = font_manager.FontProperties(fname=config.TEXT_FONT_PATH)
    else:
        text_font = font_manager.FontProperties(family='sans-serif')

    for year in years:
        dates_in_year = [d for d in sorted_dates if d.year == year]
        if not dates_in_year: continue

        raw_title = t('chart-activity-title', year=str(year))
        clean_title = _sanitize_title(raw_title)

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                fig = plt.figure(figsize=FIG_SIZE_INCHES)
                ax = fig.add_subplot(111)
                
                                                                          
                                                                            
                ax.set_xlim(date(year, 1, 1), date(year, 12, 31))
                ax.set_ylim(0, y_limit_msg)
                
                if chat_type == 'personal_chat':
                    _plot_personal_year(ax, year, dates_in_year, result, text_font)
                elif 'channel' in chat_type:
                    _plot_channel_year(ax, year, dates_in_year, result, text_font, y_limit_react)
                else:
                    _plot_group_year(ax, year, dates_in_year, result, text_font)

                         
                ax.set_title(clean_title, fontproperties=text_font, fontsize=18, pad=20)
                ax.set_xlabel(t('chart-x-label'), fontproperties=text_font, fontsize=12, labelpad=10)
                ax.grid(True, linestyle='--', alpha=0.5)
                
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    if text_font: label.set_fontproperties(text_font)
                
                                             
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                fig.autofmt_xdate()

                filename = os.path.join(output_dir, f'activity_{year}.png')
                fig.savefig(filename, dpi=CHART_DPI, bbox_inches='tight')
                plt.close(fig)

                print(t('chart-saved', filename=os.path.basename(filename)))

        except Exception as e:
            errors.append(f"Chart Error ({year}): {str(e)}")

    return errors

def _plot_group_year(ax, year, dates, result, font_prop):
    """Group: Single line for total messages."""
    counts = [result.days_activity.get(d, 0) for d in dates]
    ax.plot(dates, counts, marker='o', markersize=4, linestyle='-', linewidth=2, 
            color='tab:blue', alpha=0.8, label=t('total-msgs'))
    
    ax.set_ylabel(t('chart-y-label'), fontproperties=font_prop, fontsize=14)
    ax.legend(loc='upper left', prop=font_prop)

def _plot_channel_year(ax, year, dates, result, font_prop, y_limit_react):
    """Channel: Dual Y-axis (Posts vs Reactions)."""
    posts = [result.days_activity.get(d, 0) for d in dates]
    reactions = [result.daily_reactions.get(d, 0) for d in dates]
    
                             
    p_line = ax.plot(dates, posts, color='tab:blue', marker='o', markersize=4, 
                     linewidth=2.5, label=t('posts-label'))
    ax.set_ylabel(t('chart-y-label'), color='tab:blue', fontproperties=font_prop, fontsize=14)
    for label in ax.get_yticklabels():
        label.set_color('tab:blue')

                                    
    ax2 = ax.twinx()
    ax2.set_ylim(0, y_limit_react)
    r_line = ax2.plot(dates, reactions, color='tab:orange', marker='s', markersize=4, 
                      linewidth=1.5, linestyle='--', alpha=0.6, label=t('reactions-label'))
    
    ax2.set_ylabel(t('reactions-label'), color='tab:orange', fontproperties=font_prop, fontsize=14)
    for label in ax2.get_yticklabels():
        label.set_color('tab:orange')
        if font_prop: label.set_fontproperties(font_prop)

                     
    lines = p_line + r_line
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left', prop=font_prop)

def _plot_personal_year(ax, year, dates, result, font_prop):
    """Personal: Compare top 2 users + 'First Sender' markers."""
    participants = list(result.users_stats.keys())
    top_users = sorted(participants, key=lambda u: result.users_stats[u].total_messages, reverse=True)[:2]
    
                                                
    current_year_max = 1
    for u in top_users:
        u_counts = [result.daily_user_activity.get(d, {}).get(u, 0) for d in dates]
        if u_counts:
            current_year_max = max(current_year_max, max(u_counts))

    for i, user in enumerate(top_users):
        color = 'tab:blue' if i == 0 else 'tab:orange'
        counts = [result.daily_user_activity.get(d, {}).get(user, 0) for d in dates]
        
        ax.plot(dates, counts, label=user, color=color, linewidth=2.5, alpha=0.7)
        
                                
        starts = [d for d in dates if result.daily_first_senders.get(d) == user]
        if starts:
            y_pos = current_year_max * (1.05 + (i * 0.08))
            ax.scatter(starts, [y_pos]*len(starts), color=color, marker='v', s=40, zorder=5,
                       label=f"{t('wrote-first-short')} {user}")

    ax.set_ylabel(t('chart-y-label'), fontproperties=font_prop, fontsize=14)
    ax.legend(prop=font_prop, loc='upper left', fontsize=10)