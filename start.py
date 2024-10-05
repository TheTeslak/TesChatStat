# start.py

import sys
import os
import time
import datetime
from collections import Counter, defaultdict
import locale

import config  # Import configuration

# Import modules
from modules.data_loader import load_json_file_streaming, merge_json_files
from modules.analyzer import analyze_messages
from modules.report_generator import generate_text_report, generate_json_report
from modules.visualization import generate_personal_chat_plots, generate_group_chat_plots
from modules.config_handler import configure_in_console, save_config_to_file

def main():
    # Author links
    author_github_link = 'https://github.com/TheTeslak/TesChatStat'
    author_telegram_channel = 'https://t.me/TesNot'

    version = "Version 1.1"

    # Load available languages from the locales folder
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
    available_languages = []
    for filename in os.listdir(locales_dir):
        if filename.endswith('.py'):
            lang_code = os.path.splitext(filename)[0]
            available_languages.append(lang_code)
    current_language_index = 0  # Default to the first language in the list

    # Detect system language and default to it
    try:
        system_lang = locale.getdefaultlocale()[0]  # e.g., 'en_US'
        language_code = system_lang.split('_')[0]  # e.g., 'en'
    except:
        language_code = 'en'  # Default to English if detection fails
    if language_code in available_languages:
        current_language_index = available_languages.index(language_code)
    else:
        current_language_index = available_languages.index('en') if 'en' in available_languages else 0
    language = available_languages[current_language_index]

    # Function to load texts for the current language
    def load_texts(language_code):
        lang_module = {}
        lang_file = os.path.join(locales_dir, f'{language_code}.py')
        with open(lang_file, 'r', encoding='utf-8') as f:
            exec(f.read(), lang_module)
        return lang_module['texts']

    current_texts = load_texts(language)

    # Main loop
    while True:
        # Display ASCII art and information
        print(current_texts['ascii_art'])
        print(version)
        print(current_texts['description'])
        if config.show_author_links:
            print()
            print('⚡️')
            print(current_texts['author_links'].format(author_github_link, author_telegram_channel))
            print('⚡️')
            print()
        else:
            print()
        # Main menu
        print(current_texts['select_action'])
        for key, value in current_texts['menu_options'].items():
            print(f"{key}. {value}")
        choice = input(current_texts['prompt_choice']).strip()
        if not choice:
            choice = '1'

        if choice == '0':
            # Switch language
            current_language_index = (current_language_index + 1) % len(available_languages)
            language = available_languages[current_language_index]
            current_texts = load_texts(language)
            continue  # Show the menu again in the selected language
        elif choice == '3':
            start_time = time.time()
            merge_json_files(config.merge_folder, config.input_file, current_texts)
            elapsed_time = time.time() - start_time
            print(current_texts['processing_completed'].format(elapsed_time, config.input_file))
            input(current_texts.get('press_enter_to_return', 'Press Enter to return to the main menu...'))
            continue  # Return to main menu
        elif choice == '1' or choice == '2':
            save_json = True if choice == '2' else False

            # Load the JSON file here to determine chat type
            input_file = config.input_file
            try:
                # Get file size
                file_size_bytes = os.path.getsize(input_file)
                file_size_mb = file_size_bytes / (1024 * 1024)
                file_size_gb = file_size_bytes / (1024 * 1024 * 1024)
                # Display warnings based on file size
                if file_size_mb > 50 and file_size_gb < 1:
                    print(current_texts['file_size_warning'].format(round(file_size_mb, 2)))
                elif file_size_gb >= 1:
                    print(current_texts['file_size_large_warning'].format(round(file_size_gb, 2)))
                # Load JSON data
                header_data = load_json_file_streaming(input_file, header_only=True)
                if not header_data:
                    print(current_texts['invalid_json'])
                    input(current_texts.get('press_enter_to_return', 'Press Enter to return to the main menu...'))
                    continue
            except FileNotFoundError:
                print(current_texts['file_not_found'].format(input_file))
                input(current_texts.get('press_enter_to_return', 'Press Enter to return to the main menu...'))
                continue

            # Determine chat type
            chat_type = header_data.get('type', 'group')  # Default to 'group' if not specified
            is_personal_chat = chat_type == 'personal_chat'

            # Now proceed to configuration
            config_choice = input(current_texts['config_prompt']).strip()
            if not config_choice:
                config_choice = '1'
            if config_choice == '1':
                # Use standard config
                temp_config = vars(config).copy()
            elif config_choice == '2':
                # Configure in console, pass is_personal_chat flag
                temp_config = configure_in_console(config, current_texts, is_personal_chat)
                # Optionally save config
                save_config_choice = input(current_texts['save_config_prompt']).strip().lower()
                if save_config_choice == 'y' or save_config_choice == 'д':
                    save_config_to_file(temp_config)
            else:
                continue  # Invalid choice, show menu again

            # Start analysis
            print(current_texts['start_analysis'])
            start_time = time.time()

            # Analyze messages using streaming parsing
            analysis_results, error_info = analyze_messages(input_file, temp_config, current_texts, is_personal_chat, use_streaming=True)

            # Check if there are any messages to analyze
            if not analysis_results.get('total_messages', 0):
                print(current_texts['no_messages'])
                input(current_texts.get('press_enter_to_return', 'Press Enter to return to the main menu...'))
                continue

            # Prepare output filename
            chat_name_raw = analysis_results['chat_name']
            chat_name = chat_name_raw.replace(' ', '_').replace('/', '_')
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_filename = temp_config['output_filename_pattern'].replace('<chat_name>', chat_name).replace('<timestamp>', timestamp)

            # Generate reports
            generate_text_report(analysis_results, temp_config, current_texts, output_filename, author_github_link, author_telegram_channel, is_personal_chat)
            if save_json:
                json_output_filename = output_filename.replace('.txt', '.json')
                generate_json_report(analysis_results, json_output_filename)

            # Generate communication dynamics graphs
            if is_personal_chat:
                plot_filename_template = output_filename.replace('.txt', '_plot_<year>.png')
                generate_personal_chat_plots(analysis_results, plot_filename_template, temp_config, current_texts)
                # Inform the user about saved graphs
                years = sorted(set(date.year for date in analysis_results['daily_user_messages'].keys()))
                for year in years:
                    plot_filename = plot_filename_template.replace('<year>', str(year))
                    print(current_texts['communication_graph_saved'].format(plot_filename))
            else:
                # For group chats, generate communication statistics plots
                plot_filename_template = output_filename.replace('.txt', '_group_plot_<year>.png')
                generate_group_chat_plots(analysis_results, plot_filename_template, temp_config, current_texts)
                # Inform the user about saved graphs
                years = sorted(set(date.year for date in analysis_results['date_messages'].keys()))
                for year in years:
                    plot_filename = plot_filename_template.replace('<year>', str(year))
                    print(current_texts['communication_graph_saved'].format(plot_filename))

            elapsed_time = time.time() - start_time
            print(current_texts['processing_completed'].format(elapsed_time, output_filename))

            # Handle errors
            errors, unprocessed_messages, total_messages = error_info['errors'], error_info['unprocessed_messages'], analysis_results['total_messages']
            if unprocessed_messages > 0:
                unprocessed_percentage = (unprocessed_messages / total_messages) * 100
                if len(errors) > 10:
                    error_log_filename = f"error_logs_{chat_name}_{timestamp}.txt"
                    with open(error_log_filename, 'w', encoding='utf-8') as error_log:
                        error_log.writelines(errors)
                    print(current_texts['unprocessed_messages'].format(unprocessed_percentage))
                    print(current_texts['error_count'].format(len(errors), error_log_filename))
                else:
                    print(current_texts['unprocessed_messages'].format(unprocessed_percentage))
                    for error in errors:
                        print(error)
            if temp_config.get('show_author_links', True):
                print()
                print('⚡️')
                print(current_texts['author_links'].format(author_github_link, author_telegram_channel))
                print('⚡️')
            input(current_texts.get('press_enter_to_return', 'Press Enter to return to the main menu...'))

        else:
            continue  # Invalid choice, show menu again

if __name__ == "__main__":
    main()