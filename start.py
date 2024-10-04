# start.py

import sys
import os
import time
import json
import datetime
from collections import Counter, defaultdict

import config  # Import configuration

# Import modules
from modules.data_loader import load_json_file, merge_json_files
from modules.analyzer import analyze_messages
from modules.report_generator import generate_text_report, generate_json_report
from modules.visualization import generate_personal_chat_plots
from modules.config_handler import configure_in_console, save_config_to_file

def main():
    # Author links
    author_github_link = 'https://github.com/TheTeslak'
    author_telegram_channel = 'https://t.me/TesNot'

    version = "Version 1.0"

    ascii_art = "\033[32m" + r"""
  _______         _____ _           _    _____ _        _
 |__   __|       / ____| |         | |  / ____| |      | |
    | | ___  ___| |    | |__   __ _| |_| (___ | |_ __ _| |_
    | |/ _ \/ __| |    | '_ \ / _` | __|\___ \| __/ _` | __|
    | |  __/\__ \ |____| | | | (_| | |_ ____) | || (_| | |_
    |_|\___||___/\_____|_| |_|\__,_|\__|_____/ \__\__,_|\__|
""" + "\033[0m"  # Reset color

    # Texts in two languages
    texts = {
        'ru': {
            'ascii_art': ascii_art,
            'description': "Статистика чата Telegram на основе JSON-экспорта",
            'menu_options': {
                '0': "Switch to English",
                '1': f"Анализировать файл {config.input_file}",
                '2': "Анализировать и сохранить результат в TXT и JSON файлы",
                '3': f"Объединить файлы resultЦИФРА.json и сохранить в {config.input_file}"
            },
            'prompt_choice': "Введите номер выбора и нажмите Enter (по умолчанию 1): ",
            'start_analysis': "Запуск анализа...",
            'start_analysis_save': "Запуск анализа и сохранение в текстовый и JSON файлы...",
            'file_not_found': "Файл '{0}' не найден.",
            'file_size_warning': "Файл размером {0} МБ, обработка займёт время.",
            'invalid_json': "Ошибка: Неверный формат JSON файла.",
            'no_messages': "Файл не содержит сообщений для анализа.",
            'total_messages': "Общее количество сообщений в чате: {0}",
            'processing_completed': "Анализ завершён за {0:.2f} секунд. Результаты сохранены в файл '{1}'.",
            'unprocessed_messages': "Не удалось обработать {0:.2f}% сообщений.",
            'error_count': "Количество ошибок: {0}. Подробности в '{1}'.",
            'author_links': "⚡️ GitHub: {0}\n⚡️ Телеграм-канал: {1}",
            'select_action': "Действие:",
            'processing': "Обработано {0}/{1} сообщений... {2}",
            'date_range': "",
            'non_consecutive': "не подряд",
            'symbols': "символов",
            'avg_symbols_in_message': "Символов в сообщении",
            'voice_messages': "Голосовых",
            'forwards': "Пересланных",
            'pictures': "Изображений",
            'videos': "Видео",
            'audios': "Аудио",
            'files': "Файлы",
            'stickers': "Стикеров",
            'commands': "Команд",
            'emojis': "Эмодзи",
            'profanity_messages': "Сообщений с нецензурной лексикой",
            'top_participants': "Топ участников",
            'top_words': "Топ слов",
            'times': "раз",
            'activity': "Активность",
            'most_active_days': "Самые активные дни",
            'messages': "сообщений",
            'average_message_length': "средняя длина сообщения",
            'polls': "Опросов",
            'links': "Ссылки",
            'config_prompt': "1. Использовать стандартную настройку из config.py\n2. Настроить в консоли\nВведите номер выбора и нажмите Enter (по умолчанию 1): ",
            'save_config_prompt': "Сохранить эти настройки в файл confignew.py? (y/n, по умолчанию n): ",
            'creator_info': "Создатель группы: {0}, ID: {1}",
            'title_changes': "Изменений заголовка: {0}",
            'invite_top': "Топ пользователей по приглашениям",
            'personal_chat_stats': "{0} писал чаще: {1} сообщений\n{2}: {3} сообщений",
            'reading_time_estimate': "Чтобы прочитать всю переписку, вам понадобится примерно {0} секунд. Это {1} минут или {2} часов{3}.",
            'includes_media': "Включая медиа-файлы: {0}",
            'hours': "часов",
            'days': "или {0} дней",
            'communication_graph_saved': "График динамики общения сохранён в '{0}'.",
        },
        'en': {
            'ascii_art': ascii_art,
            'description': "Telegram chat statistics based on JSON export",
            'menu_options': {
                '0': "Переключиться на русский",
                '1': f"Analyze file {config.input_file}",
                '2': "Analyze and save results to TXT and JSON files",
                '3': f"Merge resultNUMBER.json files and save to {config.input_file}"
            },
            'prompt_choice': "Enter your choice number and press Enter (default is 1): ",
            'start_analysis': "Starting analysis...",
            'start_analysis_save': "Starting analysis and saving to text and JSON files...",
            'file_not_found': "File '{0}' not found.",
            'file_size_warning': "File size is {0} MB, processing may take some time.",
            'invalid_json': "Error: Invalid JSON file format.",
            'no_messages': "The file contains no messages for analysis.",
            'total_messages': "Total messages in chat: {0}",
            'processing_completed': "Analysis completed in {0:.2f} seconds. Results saved to '{1}'.",
            'unprocessed_messages': "Failed to process {0:.2f}% of messages.",
            'error_count': "Number of errors: {0}. Details in '{1}'.",
            'author_links': "GitHub: {0}\nTelegram channel: {1}",
            'select_action': "Select an action:",
            'processing': "Processed {0}/{1} messages... {2}",
            'date_range': "",
            'non_consecutive': "not consecutive",
            'symbols': "symbols",
            'avg_symbols_in_message': "Symbols per message",
            'voice_messages': "Voice messages",
            'forwards': "Forwards",
            'pictures': "Pictures",
            'videos': "Videos",
            'audios': "Audios",
            'files': "Files",
            'stickers': "Stickers",
            'commands': "Commands",
            'emojis': "Emoji",
            'profanity_messages': "Messages with profanity",
            'top_participants': "Top participants",
            'top_words': "Top words",
            'times': "times",
            'activity': "Activity",
            'most_active_days': "Most active days",
            'messages': "messages",
            'average_message_length': "average message length",
            'polls': "Polls",
            'links': "Links",
            'config_prompt': "1. Use standard settings from config.py\n2. Configure in console\nEnter your choice number and press Enter (default is 1): ",
            'save_config_prompt': "Save these settings to confignew.py? (y/n, default n): ",
            'creator_info': "Group creator: {0}, ID: {1}",
            'title_changes': "Title changes: {0}",
            'invite_top': "Top users by invitations",
            'personal_chat_stats': "{0} wrote more: {1} messages\n{2}: {3} messages",
            'reading_time_estimate': "To read the entire conversation, you will need approximately {0} seconds. This is {1} minutes or {2} hours{3}.",
            'includes_media': "Including media files: {0}",
            'hours': "hours",
            'days': " or {0} days",
            'communication_graph_saved': "Communication dynamics graph saved to '{0}'.",
        }
    }

    language = 'ru'  # Default language is Russian
    current_texts = texts[language]

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
            language = 'en' if language == 'ru' else 'ru'
            current_texts = texts[language]
            continue  # Show the menu again in the selected language
        elif choice == '3':
            start_time = time.time()
            merge_json_files(config.merge_folder, config.input_file, current_texts)
            elapsed_time = time.time() - start_time
            if language == 'ru':
                print(f"Объединение завершено за {elapsed_time:.2f} секунд.")
            else:
                print(f"Merging completed in {elapsed_time:.2f} seconds.")
            return
        elif choice == '1' or choice == '2':
            save_json = True if choice == '2' else False

            # Load the JSON file here to determine chat type
            input_file = config.input_file
            try:
                data = load_json_file(input_file)
            except FileNotFoundError:
                print(current_texts['file_not_found'].format(input_file))
                return
            except json.JSONDecodeError:
                print(current_texts['invalid_json'])
                return

            # Determine chat type
            chat_type = data.get('type', 'group')  # Default to 'group' if not specified
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
                if save_config_choice == 'y':
                    save_config_to_file(temp_config)
            else:
                continue  # Invalid choice, show menu again

            # Start analysis
            print(current_texts['start_analysis'])
            start_time = time.time()

            analysis_results, error_info = analyze_messages(data, temp_config, current_texts, is_personal_chat)

            # Check if there are any messages to analyze
            if not analysis_results.get('total_messages', 0):
                print(current_texts['no_messages'])
                return

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

            # Generate communication dynamics graphs for personal chats per year
            if is_personal_chat:
                plot_filename_template = output_filename.replace('.txt', '_plot_<year>.png')
                generate_personal_chat_plots(analysis_results, plot_filename_template, temp_config)
                # Inform the user about saved graphs
                years = sorted(set(date.year for date in analysis_results['daily_user_messages'].keys()))
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

            return

        else:
            continue  # Invalid choice, show menu again

if __name__ == "__main__":
    main()