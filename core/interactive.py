import config
from core.i18n import t
from core.settings_manager import save_settings
from datetime import datetime
from typing import Optional

def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except ValueError:
        return None

def prompt_bool(text: str, default: bool) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{text} {suffix}: ").strip().lower()
    if not raw: return default
    return raw.startswith('y') or raw.startswith('д')

def prompt_str(text: str, default: str, allowed: list = None) -> str:
    raw = input(f"{text} [{default}]: ").strip()
    if not raw: return default
    if allowed and raw not in allowed:
        print(t('cli-invalid-choice', default=default))
        return default
    return raw

def prompt_int(text: str, default: int) -> int:
    raw = input(f"{text} [{default}]: ").strip()
    if not raw: return default
    try:
        return int(raw)
    except ValueError:
        return default

def configure_interactive():
    """
    Interactive Wizard. Collects settings and saves to JSON.
    """
    print(f"\n{t('cli-config-title')}")
    
    new_conf = {}

                   
    print(f"\n{t('cli-date-prompt')}")
    hint = t('cli-date-hint')
    date_range = input(f"   {hint}: ").strip()
    
    if date_range:
        parts = date_range.split('-')
        if len(parts) == 2:
            s_date = parse_date(parts[0])
            e_date = parse_date(parts[1])
            if s_date and e_date:
                new_conf['START_DATE'] = s_date
                new_conf['END_DATE'] = e_date
                print(f"   {t('cli-range-set', start=parts[0], end=parts[1])}")
        else:
            print(f"   {t('cli-invalid-format')}")

                        
    new_conf['ANALYSIS_LANGUAGE'] = prompt_str(f"\n{t('cli-lang-prompt')}", config.ANALYSIS_LANGUAGE, ['ru', 'en'])
    new_conf['TIME_OFFSET'] = prompt_int(f"{t('cli-offset-prompt')}", config.TIME_OFFSET)

                             
    new_conf['NEW_DIALOG_THRESHOLD_HOURS'] = prompt_int(f"{t('cli-threshold-prompt')}", config.NEW_DIALOG_THRESHOLD_HOURS)

                                 
    lang = new_conf.get('ANALYSIS_LANGUAGE', config.ANALYSIS_LANGUAGE)
    if lang == 'ru':
        print(f"\n{t('cli-sw-title')}")
        print(f"   1. {t('cli-sw-minimal')} (Grammar only)")
        print(f"   2. {t('cli-sw-extended')} (Semantic noise removal)")
        
        current_type = getattr(config, 'STOP_WORDS_TYPE', 'extended')
        default_idx = '2' if current_type == 'extended' else '1'
        
        sw_choice = input(f"   {t('cli-choice-input')} [{default_idx}]: ").strip()
        if not sw_choice: sw_choice = default_idx
        
        if sw_choice == '2':
            new_conf['STOP_WORDS_TYPE'] = 'extended'
        else:
            new_conf['STOP_WORDS_TYPE'] = 'minimal'
            
                                      
        merge_en = prompt_bool(f"   {t('cli-merge-en-prompt', default='Remove English noise?')}", getattr(config, 'MERGE_ENGLISH_STOPWORDS', True))
        new_conf['MERGE_ENGLISH_STOPWORDS'] = merge_en
                                 

             
    new_conf['EXCLUDE_BOTS'] = prompt_bool(f"\n{t('cli-bots-prompt')}", config.EXCLUDE_BOTS)

                        
    lemmatize = prompt_bool(f"\n{t('cli-lemmatize-prompt')}", False)
    new_conf['LEMMATIZE_WORDS'] = lemmatize
    
    new_conf['GENERATE_WORDCLOUD'] = prompt_bool(f"{t('cli-cloud-prompt')}", config.GENERATE_WORDCLOUD)
    
                
    print(f"\n{t('cli-sort-prompt')}:")
    print(f"   1. Messages")
    print(f"   2. Symbols")
    print(f"   3. Active Days")
    s_choice = input(f"   {t('cli-choice-input')} [1]: ").strip()
    
    if s_choice == '2': new_conf['PARTICIPANT_SORT_BY'] = 'symbols'
    elif s_choice == '3': new_conf['PARTICIPANT_SORT_BY'] = 'active_days'
    else: new_conf['PARTICIPANT_SORT_BY'] = 'messages'

                    
    new_conf['FULL_JSON_EXPORT'] = prompt_bool(f"\n{t('cli-full-json-prompt')}", config.FULL_JSON_EXPORT)

    print("-" * 30)
    print(f"{t('cli-config-applied')}")
    
               
    print("")
    if prompt_bool(t('cli-save-prompt'), True):
        success = save_settings(new_conf)
        if success:
            print(t('cli-saved'))
                                             
            for k, v in new_conf.items():
                setattr(config, k, v)
        else:
            print(t('cli-save-error', error="IOError"))
    print("")