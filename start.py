import sys
import threading
from typing import Optional

if sys.version_info < (3, 10):
    print("❌ Critical Error: Kmetrum requires Python 3.10 or higher.")
    sys.exit(1)

import os
import time
import locale
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import font_manager

import config
from core.constants import GITHUB_REPO_URL, TELEGRAM_CHANNEL_URL, APP_VERSION

from core.settings_manager import load_settings
from core.loader import load_json_header, stream_messages, autodetect_input_file
from core.serializer import save_result_to_json
from core.normalizer import load_word_list
from core.i18n import init_i18n, t
from core.interactive import configure_interactive
from core.types import ChatMetadata

                                           
from core.updater import check_for_updates, print_update_banner, RemoteStatus

from analyzers import get_analyzer
from reporters import get_reporter
from reporters.visualizers.charts import generate_activity_chart
from reporters.visualizers.cloud import generate_word_cloud
from reporters.visualizers.heatmap import generate_heatmap

                                                       
_update_status: Optional[RemoteStatus] = None

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_dynamic_status(text: str):
    sys.stdout.write(f"\r\033[K⠋  {text}")
    sys.stdout.flush()

def clear_dynamic_status():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

def get_dir_size_mb(path: str) -> float:
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass
    return total_size / (1024 * 1024)

def print_banner():
    print("\033[32m" + t('ascii-art') + "\033[0m")
    print(t('app-title', version=APP_VERSION))
    print(t('description'))
    
    if config.SHOW_AUTHOR_LINKS:
        print("") 
        print(t('link-separator'))
        print(t('link-github', url=GITHUB_REPO_URL))
        print(t('link-telegram', url=TELEGRAM_CHANNEL_URL))
        print(t('link-separator'))
        print("")

def detect_system_language():
    try:
                                                             
        for var in ('LC_ALL', 'LC_MESSAGES', 'LANG', 'LANGUAGE'):
            val = os.environ.get(var)
            if val and 'ru' in val.lower():
                return 'ru'
        
                                      
        if os.name == 'nt':
            import ctypes
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            if (lang_id & 0xFF) == 25:
                return 'ru'
    except Exception:
        pass
    return 'en'

def toggle_language():
    new_lang = 'en' if config.ANALYSIS_LANGUAGE == 'ru' else 'ru'
    config.ANALYSIS_LANGUAGE = new_lang
    init_i18n(new_lang)

def setup_fonts():
    if os.path.exists(config.TEXT_FONT_PATH):
        try: font_manager.fontManager.addfont(config.TEXT_FONT_PATH)
        except: pass
    if os.path.exists(config.EMOJI_FONT_PATH):
        try: font_manager.fontManager.addfont(config.EMOJI_FONT_PATH)
        except: pass

def print_smart_summary(analyzer, report_dir, elapsed_time):
    res = analyzer.result
    date_str = "..."
    if res.first_date and res.last_date:
        if res.first_date.year != res.last_date.year:
            date_str = f"{res.first_date.year} – {res.last_date.year}"
        else:
            date_str = f"{res.first_date.strftime('%d.%m.%Y')} – {res.last_date.strftime('%d.%m.%Y')}"
            
    dir_size = get_dir_size_mb(report_dir)
    
    summary_data = [
        (config.EMOJIS['messages'], t('sum-messages'), f"{res.global_stats.total_messages:,}".replace(",", " ")),
        (config.EMOJIS['participant'], t('sum-participants'), f"{len(res.users_stats)}"),
        (config.EMOJIS['active_days'], t('sum-period'), date_str),
        ("💾", t('sum-size'), f"{dir_size:.1f} MB"),
    ]

    max_label_len = max(len(item[1]) for item in summary_data) + 2

    print(f"📁 {report_dir}")
    print(f"⏱  {elapsed_time:.2f} s")
    print("")
    
    for icon, label, value in summary_data:
        print(f"{icon} {label.ljust(max_label_len)} {value}")

def handle_errors(errors, report_dir):
    if not errors: return

    count = len(errors)
    print("")
    
    if count < 11:
        for err in errors:
            parts = str(err).split(':', 1)
            title = parts[0]
            details = parts[1].strip() if len(parts) > 1 else ""
            print(f"⚠️  {title}")
            if details: print(f"    {details}")
            print("")
    else:
        err_filename = os.path.join(report_dir, '_errors.txt')
        try:
            with open(err_filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(errors))
            print(f"⚠️  {t('errors-hidden-notice', count=count)}")
            print(f"    📄 {err_filename}")
        except Exception as e:
            print(f"⚠️  {count} errors occurred (Failed to save log: {e})")

def run_analysis_pipeline(save_json_report=False):
    input_files, status_key = autodetect_input_file(config.INPUT_FILE)
    
    if not input_files:
        print(f"⚠️  {t(status_key, default='Input file not found')}")
        if status_key == 'err-ambiguous-files':
             print(f"    {t('hint-ambiguous', default='Rename file to result.json or configure path.')}")
        input(f"\n{t('press-enter')}")
        return
        
    main_file = input_files[0]
    
                             
    if len(input_files) > 1:
        print(f"📦 {t('multi-file-detected', count=len(input_files))}")
        print(f"   [{', '.join([os.path.basename(f) for f in input_files])}]")
    elif main_file != config.INPUT_FILE:
        print(f"ℹ️  {t('auto-detected-file', file=main_file)}")

                                                                                                    
    should_ask = (main_file != config.INPUT_FILE) or (len(input_files) > 1)

    if should_ask:
        confirm = input(f"    {t('confirm-analysis', default='Analyze these files? [Y/n] ')}").strip().lower()
        if confirm and not (confirm.startswith('y') or confirm.startswith('д')):
            print(f"\n{t('op-cancelled')}")
            return
    
    try:
        total_size_mb = sum(os.path.getsize(f) for f in input_files) / (1024 * 1024)
        if total_size_mb > 500:
            print(f"    {t('file-size-warning', size=f'{total_size_mb:.0f}')}") 
    except OSError:
        pass

    if config.LEMMATIZE_WORDS:
        print(f"⚠️  {t('warn-lemmatization-slow')}")

    msg_analyzing = t('analyzing-file', file=main_file).replace('📂', '').strip()
    print(f"🔍 {msg_analyzing}")
    
    header = load_json_header(main_file)
    if not header:
        print(t('meta-error'))
        input(f"\n{t('press-enter')}")
        return

    meta = ChatMetadata(
        chat_id=header.get('id', 0),
        name=header.get('name', 'Unknown Chat'),
        chat_type=header.get('type', 'group')
    )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = "".join([c for c in meta.name if c.isalnum() or c in (' ', '_', '-')]).strip()
    if not safe_name: safe_name = "Chat"
    
    folder_name = f"{safe_name}_{timestamp}"
    report_dir = os.path.join(config.BASE_DIR, config.REPORTS_DIR_NAME, folder_name)
    
    try:
        os.makedirs(report_dir, exist_ok=True)
    except OSError:
        report_dir = os.path.join(config.BASE_DIR, config.REPORTS_DIR_NAME, f"Chat_Export_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)

                                              
    stop_words = set()
    
                                   
    if config.ANALYSIS_LANGUAGE == 'ru':
                                                           
        if config.STOP_WORDS_TYPE == 'minimal':
            f_name = config.STOPWORDS_FILENAME_RU_MINIMAL
        else:
            f_name = config.STOPWORDS_FILENAME_RU_EXTENDED
        stop_words = load_word_list(os.path.join(config.WORDS_DIR, f_name))
    else:
                                     
        stop_words = load_word_list(os.path.join(config.WORDS_DIR, config.STOPWORDS_FILENAME_EN))

                                                            
    if config.MERGE_ENGLISH_STOPWORDS and config.ANALYSIS_LANGUAGE != 'en':
        eng_path = os.path.join(config.WORDS_DIR, config.STOPWORDS_FILENAME_EN)
        eng_words = load_word_list(eng_path)
        stop_words.update(eng_words)

                                         
    profanity_path = os.path.join(config.WORDS_DIR, config.PROFANITY_FILENAME)
    profanity_words = load_word_list(profanity_path)
                                              

    analyzer = get_analyzer(
        meta, 
        stop_words=stop_words, 
        profanity_words=profanity_words,
        start_date=config.START_DATE,
        end_date=config.END_DATE
    )
    analyzer.result.metadata = meta

    start_time = time.time()
    
    msg_gen = stream_messages(input_files)
    
    count = 0
    tqdm_fmt = "{n_fmt} msg [{elapsed}, {rate_fmt}]"
    
    try:
        with tqdm(unit=" msg", dynamic_ncols=True, bar_format=tqdm_fmt) as pbar:
            for msg in msg_gen:
                analyzer.process_message(msg)
                count += 1
                if count % 100 == 0: pbar.update(100)
            pbar.update(count % 100)
            
        analyzer.finalize()
    except KeyboardInterrupt:
        print(f"\n{t('op-cancelled')}")
        if os.path.exists(report_dir) and not os.listdir(report_dir):
            os.rmdir(report_dir)
        return
    except Exception as e:
        print(f"\n❌ {t('error-prefix', default='Error')}: {e}")
        input(f"\n{t('press-enter')}")
        return

    if count == 0:
        print(f"\n{t('no-errors')}") 
        os.rmdir(report_dir)
        input(f"\n{t('press-enter')}")
        return

    print(f"✅ {t('analysis-complete', count=f'{count:,}'.replace(',', ' '))}")

               
    set_dynamic_status(t('status-generating-report'))
    txt_filename = os.path.join(report_dir, 'report.txt')
    reporter = get_reporter(meta, analyzer.result)
    try:
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(reporter.render())
    except Exception as e:
        analyzer.result.errors.append(f"Report Generation: {str(e)}")

    if save_json_report or config.FULL_JSON_EXPORT:
        set_dynamic_status(t('status-saving-json'))
        json_filename = os.path.join(report_dir, 'data.json')
        success, err = save_result_to_json(analyzer.result, json_filename)
        if not success:
            analyzer.result.errors.append(f"JSON Export: {err}")

                   
    set_dynamic_status(t('status-visualizing'))
    setup_fonts()
    
    chart_errors = generate_activity_chart(analyzer.result, report_dir)
    analyzer.result.errors.extend(chart_errors)
    
    set_dynamic_status(t('status-visualizing-heatmap'))
    hm_err = generate_heatmap(analyzer.result, report_dir)
    if hm_err: analyzer.result.errors.append(hm_err)
    
    if config.GENERATE_WORDCLOUD:
        set_dynamic_status(t('status-visualizing-cloud'))
        wc_err = generate_word_cloud(analyzer.result, report_dir)
        if wc_err: analyzer.result.errors.append(wc_err)

    clear_dynamic_status()

    elapsed = time.time() - start_time
    print_smart_summary(analyzer, report_dir, elapsed)
    handle_errors(analyzer.result.errors, report_dir)

    input(f"\n{t('press-enter')}")

                       
def _update_checker_worker():
    """Background worker to check updates without blocking UI."""
    global _update_status
    try:
        _update_status = check_for_updates(current_lang=config.ANALYSIS_LANGUAGE)
    except Exception:
        _update_status = None

def main():
    load_settings()

    config.ANALYSIS_LANGUAGE = detect_system_language()
    init_i18n(config.ANALYSIS_LANGUAGE)

                                             
    update_thread = threading.Thread(target=_update_checker_worker, daemon=True)
    update_thread.start()

                              
    for _ in range(15):
        if _update_status is not None:
            break
        time.sleep(0.1)

    while True:
        cls()
        print_banner()
        
                                 
        if _update_status:
            print_update_banner(_update_status)
        
        print(t('select-action'))
        print(f"0. {t('menu-0-lang')} [{config.ANALYSIS_LANGUAGE.upper()}]")
        print(f"1. {t('menu-1-analyze')}")
        print(f"2. {t('menu-2-json')}")
        print(f"3. {t('menu-4-config')}")
        print(f"4. {t('menu-5-exit')}")
        
        choice = input(f"\n{t('menu-prompt')} ").strip()

        if choice == '0':
            toggle_language()
            update_thread = threading.Thread(target=_update_checker_worker, daemon=True)
            update_thread.start()
        elif choice == '1' or choice == '':
            run_analysis_pipeline(save_json_report=False)
        elif choice == '2':
            run_analysis_pipeline(save_json_report=True)
        elif choice == '3':
            configure_interactive()
        elif choice == '4':
            sys.exit(0)
        else:
            print(t('invalid-choice', default="Invalid choice"))
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{t('goodbye', default='Goodbye!')}")