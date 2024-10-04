import json
import datetime
import re
import sys
import os
from collections import Counter, defaultdict
import time

import config  # Import configuration

def is_bot(user_name, bot_identifiers):
    return any(bot_id.lower() in user_name.lower() for bot_id in bot_identifiers)

def format_number(number):
    s = str(int(number))
    return ' '.join([s[max(i - 3, 0):i] for i in range(len(s), 0, -3)][::-1])

def merge_json_files(folder_path, output_file):
    merged_data = None
    pattern = re.compile(r'^result\d+\.json$')
    if not os.path.isdir(folder_path) or folder_path == '':
        folder_path = '.'  # Use current directory if folder is not specified or does not exist
    for filename in os.listdir(folder_path):
        if pattern.match(filename):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if merged_data is None:
                        merged_data = data
                    else:
                        merged_data['messages'].extend(data.get('messages', []))
    if merged_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False)
        print(f"Файлы, соответствующие шаблону 'result*.json' в папке '{folder_path}', объединены и сохранены в '{output_file}'.")
    else:
        print("Нет данных для объединения.")

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
            'author_links': "⚡ GitHub: {0}\n⚡ Телеграм-канал: {1}",
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
            'profanity_messages': "Сообщений с матом",
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
            merge_json_files(config.merge_folder, config.input_file)
            elapsed_time = time.time() - start_time
            if language == 'ru':
                print(f"Объединение завершено за {elapsed_time:.2f} секунд.")
            else:
                print(f"Merging completed in {elapsed_time:.2f} seconds.")
            return
        elif choice == '1' or choice == '2':
            save_json = True if choice == '2' else False
            # Ask for configuration
            config_choice = input(current_texts['config_prompt']).strip()
            if not config_choice:
                config_choice = '1'
            if config_choice == '1':
                # Use standard config
                temp_config = vars(config).copy()
                break  # Start analysis
            elif config_choice == '2':
                # Configure in console
                temp_config = configure_in_console(config, current_texts)
                # Ask to save config
                save_config_choice = input(current_texts['save_config_prompt']).strip().lower()
                if save_config_choice == 'y':
                    save_config_to_file(temp_config)
                break  # Start analysis
            else:
                continue  # Invalid choice, show menu again
        else:
            continue  # Invalid choice, show menu again

    # Use temporary settings
    show_non_consecutive_counts = temp_config.get('show_non_consecutive_counts', True)
    exclude_bots = temp_config.get('exclude_bots', True)
    top_participants_count = temp_config.get('top_participants_count', None)
    top_words_count = temp_config.get('top_words_count', 100)  # Updated limit to 100
    input_file = temp_config.get('input_file', 'result.json')
    merge_folder = temp_config.get('merge_folder', '')
    output_filename_pattern = temp_config.get('output_filename_pattern', '<chat_name>_<timestamp>.txt')
    show_author_links = temp_config.get('show_author_links', True)
    show_user_links = temp_config.get('show_user_links', False)
    profanity_words = set(temp_config.get('profanity_words', []))
    commands_identifiers = set(temp_config.get('commands_identifiers', ['/']))
    emoji_pattern = temp_config.get('emoji_pattern', re.compile("["
                            u"\U0001F600-\U0001F64F"
                            u"\U0001F300-\U0001F5FF"
                            u"\U0001F680-\U0001F6FF"
                            u"\U0001F1E0-\U0001F1FF"
                            u"\U0001F900-\U0001F9FF"
                            u"\U0001FA70-\U0001FAFF"
                            u"\U00002702-\U000027B0"
                            u"\U000024C2-\U0001F251"
                            "]+", flags=re.UNICODE))
    url_pattern = temp_config.get('url_pattern', re.compile(
        r'(?i)\b((?:https?:\/\/|www\d{0,3}[.]|telegram[.]me\/|t[.]me\/|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+)', re.IGNORECASE))
    stop_words = set(temp_config.get('stop_words', []))
    # Добавляем английские стоп-слова
    stop_words.update({'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 'for', 'on', 'are', 'with', 'as', 'i', 'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from'})

    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(current_texts['file_not_found'].format(input_file))
        return

    # Rest of the code remains similar, with necessary adjustments
    # ...

    # Begin analysis
    print(current_texts['start_analysis'])
    start_time = time.time()

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(current_texts['invalid_json'])
        return

    # Determine chat type
    chat_type = data.get('type', 'group')  # Default to 'group' if not specified
    is_personal_chat = chat_type == 'personal_chat'

    # Extract messages
    messages = data.get('messages', [])
    total_messages = len(messages)
    total_messages_formatted = format_number(total_messages)
    print(current_texts['total_messages'].format(total_messages_formatted))

    if total_messages == 0:
        print(current_texts['no_messages'])
        return

    # Initialize variables
    user_messages = []
    first_date = None
    last_date = None

    # Initialize message counts
    message_counts = {
        'text': 0,
        'sticker': 0,
        'picture': 0,
        'video': 0,
        'gif': 0,
        'voice_message': 0,
        'audio': 0,
        'file': 0,
        'commands': 0,
        'forwards': 0,
        'emojis': 0,
        'profanity': 0,
        'replies': 0,
        'poll': 0,
        'links': 0,
    }

    user_counts = Counter()
    user_symbols = Counter()
    non_consecutive_counts = Counter()
    user_ids = {}
    prev_user = None
    prev_time = None
    user_response_times = defaultdict(list)
    words = []
    hours = Counter()
    weekdays = Counter()
    months = Counter()
    years = Counter()
    dates = Counter()
    date_messages = defaultdict(int)
    date_symbols = defaultdict(int)
    # New variables for personal chat
    user_intervals = defaultdict(list)  # For intervals of inactivity
    # For invitation tracking
    invite_counts = Counter()
    title_change_count = 0
    creator_name = None
    creator_id = None
    includes_media = 0  # For estimating reading time

    # Compile patterns once
    unprocessed_messages = 0
    error_count = 0

    # Prepare error log file
    chat_name = data.get('name', 'Chat Name').replace(' ', '_').replace('/', '_')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    error_log_filename = f"error_logs_{chat_name}_{timestamp}.txt"
    error_log = open(error_log_filename, 'w', encoding='utf-8')

    # Spinner for progress
    spinner = ['|', '/', '-', '\\']
    spinner_index = 0

    def print_progress(current, total):
        nonlocal spinner_index
        current_formatted = format_number(current)
        total_formatted = format_number(total)
        progress = current_texts['processing'].format(current_formatted, total_formatted, spinner[spinner_index % len(spinner)])
        spinner_index += 1
        print(progress, end='\r', flush=True)

    total_messages = len(messages)

    chain_started = False  # For non-consecutive message counting
    for idx, message in enumerate(messages):
        try:
            if 'from' not in message and 'actor' not in message:
                unprocessed_messages += 1
                continue
            user = message.get('from', '') or message.get('actor', 'Unknown')
            from_id = message.get('from_id', '') or message.get('actor_id', '') or message.get('id', '')
            if from_id:
                if isinstance(from_id, str):
                    if from_id.startswith('user'):
                        user_id = from_id.replace('user', '')
                    elif from_id.startswith('channel'):
                        user_id = from_id.replace('channel', '')
                    else:
                        user_id = from_id
                else:
                    user_id = str(from_id)
                user_ids[user] = user_id
            else:
                user_id = ''
                user_ids[user] = user_id

            # Exclude bots only in group chats
            if not is_personal_chat and exclude_bots and is_bot(user, config.bot_identifiers):
                continue
            text = message.get('text', '')
            if isinstance(text, list):
                text_pieces = []
                for t_piece in text:
                    if isinstance(t_piece, dict):
                        text_pieces.append(t_piece.get('text', ''))
                    elif isinstance(t_piece, str):
                        text_pieces.append(t_piece)
                text = ''.join(text_pieces)
            elif text is None:
                text = ''
            symbols = len(text)
            message_type = message.get('type', '')

            if message_type == 'message':
                user_messages.append(message)
                user_counts[user] += 1
                user_symbols[user] += symbols

                if prev_user != user:
                    non_consecutive_counts[user] += 1
                    chain_started = True
                else:
                    chain_started = False

                # Calculate response time between messages of different users
                message_date = message.get('date')
                if message_date:
                    try:
                        date_time = datetime.datetime.fromisoformat(message_date)
                        if first_date is None or date_time < first_date:
                            first_date = date_time
                        if last_date is None or date_time > last_date:
                            last_date = date_time

                        # For personal chat, track intervals of inactivity greater than 1 hour
                        if is_personal_chat:
                            if prev_time:
                                delta = date_time - prev_time
                                if delta.total_seconds() > 3600:
                                    user_intervals[user].append(delta.total_seconds())
                        prev_time = date_time

                        hours[date_time.hour] += 1
                        weekday_index = date_time.weekday()
                        weekday_name = config.day_names[language][weekday_index]
                        weekdays[weekday_name] += 1
                        month_name = f"{config.month_names[language][date_time.month -1]} {date_time.year}"
                        months[month_name] +=1
                        years[date_time.year] +=1
                        date_only = date_time.date()
                        dates[date_only] += 1
                        date_messages[date_only] += 1
                        date_symbols[date_only] += symbols
                    except (ValueError, KeyError) as e:
                        error_count +=1
                        error_log.write(f"Error processing date in message id {message.get('id')}: {e}\n")
                else:
                    prev_time = None

                prev_user = user

                # Collect words
                if text:
                    text_clean = re.sub(r'[^\w\s]', '', text.lower())
                    words.extend([word for word in text_clean.split() if word not in stop_words and word.isalpha()])

                    # Check for commands
                    if text.strip().startswith(tuple(commands_identifiers)):
                        message_counts['commands'] += 1

                    # Check for emojis
                    if emoji_pattern.search(text):
                        message_counts['emojis'] += 1

                    # Check for profanity
                    if profanity_words.intersection(set(text_clean.split())):
                        message_counts['profanity'] += 1

                    # Check for links
                    if url_pattern.search(text):
                        message_counts['links'] +=1

                # Check for forwarded messages
                if 'forwarded_from' in message:
                    message_counts['forwards'] += 1

                # Check for replies
                if 'reply_to_message_id' in message:
                    message_counts['replies'] += 1

                # Check for polls
                if 'poll' in message:
                    message_counts['poll'] += 1

                # Count media types
                if 'media_type' in message:
                    media_type = message['media_type']
                    if media_type == 'sticker':
                        message_counts['sticker'] += 1
                        includes_media += 1
                    elif media_type == 'photo':
                        message_counts['picture'] += 1
                        includes_media += 1
                    elif media_type == 'video_file':
                        file_name = message.get('file', '') or message.get('file_name', '')
                        if 'gif' in file_name.lower():
                            message_counts['gif'] += 1
                        else:
                            message_counts['video'] += 1
                        includes_media += 1
                    elif media_type == 'voice_message' or media_type == 'video_message':
                        message_counts['voice_message'] += 1
                        includes_media += 1
                    elif media_type == 'audio_file':
                        message_counts['audio'] += 1
                        includes_media += 1
                    elif media_type == 'document':
                        mime_type = message.get('mime_type', '')
                        if mime_type.startswith('image/'):
                            message_counts['picture'] += 1
                        else:
                            message_counts['file'] += 1
                        includes_media += 1
                    elif media_type == 'animation':
                        message_counts['gif'] +=1
                        includes_media += 1
                else:
                    # If 'media_type' is not present, but message contains media
                    if 'photo' in message:
                        message_counts['picture'] += 1
                        includes_media += 1
                    elif 'file' in message:
                        mime_type = message.get('mime_type', '')
                        if mime_type.startswith('image/'):
                            message_counts['picture'] += 1
                        else:
                            message_counts['file'] += 1
                        includes_media += 1
                    else:
                        message_counts['text'] += 1

            elif message_type == 'service':
                action = message.get('action', '')
                if action == 'create_group':
                    creator_name = message.get('actor', '')
                    creator_id = message.get('actor_id', '')
                    if isinstance(creator_id, str) and creator_id.startswith('user'):
                        creator_id = creator_id.replace('user', '')
                elif action == 'invite_member' or action == 'invite_members':
                    inviter = message.get('actor', 'Unknown')
                    invite_counts[inviter] += 1
                elif action == 'edit_title':
                    title_change_count +=1
                else:
                    pass  # Handle other service actions if needed
            else:
                unprocessed_messages += 1
                continue

            # Update progress
            if total_messages > 0 and idx % 1000 == 0:
                print_progress(idx, total_messages)

        except Exception as e:
            unprocessed_messages += 1
            error_count += 1
            msg_id = message.get('id', 'Unknown')
            error_log.write(f"Error processing message id {msg_id}: {e}\n")

    error_log.close()

    print_progress(total_messages, total_messages)
    print('\n')

    # Calculate statistics
    total_msgs = sum(user_counts.values())
    total_symbols = sum(user_symbols.values())
    avg_message_length = total_symbols / total_msgs if total_msgs else 0
    common_words = Counter(words).most_common(top_words_count)
    activity = {
        'hours': hours.most_common(3) if hours else [],
        'weekdays': weekdays.most_common(3) if weekdays else [],
        'months': months.most_common(3) if months else [],
        'years': years.most_common(3) if years else [],
    }
    avg_response = {}
    for user, times in user_response_times.items():
        if times:
            avg_response[user] = sum(times) / len(times)
        else:
            avg_response[user] = 0

    # Top most active days
    top_days = dates.most_common(config.top_days_count)

    # Calculate percentage of unprocessed messages
    unprocessed_percentage = (unprocessed_messages / total_messages) * 100 if total_messages else 0

    # Format output file name
    output_filename = output_filename_pattern.replace('<chat_name>', chat_name).replace('<timestamp>', timestamp)

    # Prepare data for JSON output
    json_output_data = {
        'chat_name': data.get('name', 'Chat Name'),
        'date_range': '',
        'message_counts': message_counts,
        'users': [
            {
                'name': user,
                'count': user_counts[user],
                'symbols': user_symbols[user],
                'non_consecutive_count': non_consecutive_counts[user],
                'id': user_ids.get(user, '')
            }
            for user in user_counts
        ],
        'common_words': common_words,
        'activity': activity,
        'top_days': [(date.strftime('%d.%m.%Y'), msg_count) for date, msg_count in top_days],
    }

    # Start writing to the output file
    with open(output_filename, 'w', encoding='utf-8') as f:
        # Header
        date_range_str = ''
        if first_date and last_date:
            date_range_str = f"за период: {first_date.strftime('%d.%m.%Y')} – {last_date.strftime('%d.%m.%Y')}"
            json_output_data['date_range'] = f"{first_date.strftime('%d.%m.%Y')} - {last_date.strftime('%d.%m.%Y')}"
        f.write(f"Статистика чата \"{data.get('name', 'Chat Name')}\" {date_range_str}\n\n")

        # Messages and symbols statistics
        if show_non_consecutive_counts:
            f.write(f"{config.emojis.get('messages','')} {current_texts['messages'].capitalize()}: {format_number(total_msgs)} ({format_number(sum(non_consecutive_counts.values()))} {current_texts.get('non_consecutive', 'not consecutive')})\n")
            f.write(f"{config.emojis.get('symbols','')} {current_texts.get('symbols', 'symbols').capitalize()}: {format_number(total_symbols)}\n")
        else:
            f.write(f"{config.emojis.get('messages','')} {current_texts['messages'].capitalize()}: {format_number(total_msgs)}\n")
            f.write(f"{config.emojis.get('symbols','')} {current_texts.get('symbols', 'symbols').capitalize()}: {format_number(total_symbols)}\n")
        f.write(f"{config.emojis.get('avg_symbols','')} {current_texts.get('avg_symbols_in_message', 'Symbols per message')}: {avg_message_length:.0f}\n\n")

        # Message counts by type
        f.write(f"{config.emojis.get('pictures','')} {current_texts.get('pictures', 'Pictures')}: {format_number(message_counts['picture'])}\n")
        f.write(f"{config.emojis.get('videos','')} {current_texts.get('videos', 'Videos')}: {format_number(message_counts['video'])}\n")
        f.write(f"{config.emojis.get('files','')} {current_texts.get('files', 'Files')}: {format_number(message_counts['file'])}\n")
        f.write(f"{config.emojis.get('audios','')} {current_texts.get('audios', 'Audios')}: {format_number(message_counts['audio'])}\n")
        f.write(f"{config.emojis.get('links','')} {current_texts.get('links', 'Links')}: {format_number(message_counts['links'])}\n")
        f.write(f"{config.emojis.get('voice','')} {current_texts.get('voice_messages', 'Voice messages')}: {format_number(message_counts['voice_message'])}\n")
        f.write(f"{config.emojis.get('gif','')} GIF: {format_number(message_counts['gif'])}\n")
        f.write(f"{config.emojis.get('sticker','')} {current_texts.get('stickers', 'Stickers')}: {format_number(message_counts['sticker'])}\n")
        f.write(f"{config.emojis.get('emoji','')} {current_texts.get('emojis', 'Emoji')}: {format_number(message_counts['emojis'])}\n")
        f.write(f"{config.emojis.get('poll','')} {current_texts.get('polls', 'Polls')}: {format_number(message_counts['poll'])}\n")
        f.write(f"{config.emojis.get('command','')} {current_texts.get('commands', 'Commands')}: {format_number(message_counts['commands'])}\n")
        f.write(f"{config.emojis.get('profanity','')} {current_texts.get('profanity_messages', 'Messages with profanity')}: {format_number(message_counts['profanity'])}\n\n")

        # For personal chats
        if is_personal_chat:
            participants = list(user_counts.keys())
            if len(participants) == 2:
                user1, user2 = participants
                count1 = user_counts[user1]
                count2 = user_counts[user2]
                if count1 > count2:
                    f.write(f"{current_texts['personal_chat_stats'].format(user1, format_number(count1), user2, format_number(count2))}\n")
                else:
                    f.write(f"{current_texts['personal_chat_stats'].format(user2, format_number(count2), user1, format_number(count1))}\n")
                # Estimate reading time (assuming average reading speed)
                total_reading_seconds = (total_symbols / 1000) * 60  # Assuming 1000 chars per minute
                total_reading_minutes = total_reading_seconds / 60
                total_reading_hours = total_reading_minutes / 60
                total_reading_days = total_reading_hours / 24
                total_reading_days_formatted = f"{total_reading_days:.2f}" if total_reading_days >= 1 else ""
                days_part = current_texts['days'].format(total_reading_days_formatted) if total_reading_days_formatted else ""
                f.write(f"\n{current_texts['reading_time_estimate'].format(int(total_reading_seconds), int(total_reading_minutes), int(total_reading_hours), days_part)}\n")
                # 'Includes_media' line is removed as per request
            else:
                f.write("Unexpected number of participants in personal chat.\n")
        else:
            # Top participants
            f.write(f"{config.emojis.get('participant', '')} {current_texts.get('top_participants', 'Top participants')}:\n")
            sorted_users = user_counts.most_common(top_participants_count)
            rank = 1
            for user, count in sorted_users:
                non_consecutive_count = non_consecutive_counts[user]
                symbols = user_symbols[user]
                user_id = user_ids.get(user, '')
                if show_non_consecutive_counts:
                    if show_user_links:
                        user_link = f"tg://openmessage?user_id={user_id}" if user_id else ''
                        f.write(f"{rank}. {user} ({user_link}): {format_number(count)} ({format_number(non_consecutive_count)}) · {format_number(symbols)}\n")
                    else:
                        f.write(f"{rank}. {user}: {format_number(count)} ({format_number(non_consecutive_count)}) · {format_number(symbols)}\n")
                else:
                    if show_user_links:
                        user_link = f"tg://openmessage?user_id={user_id}" if user_id else ''
                        f.write(f"{rank}. {user} ({user_link}): {format_number(count)} · {format_number(symbols)}\n")
                    else:
                        f.write(f"{rank}. {user}: {format_number(count)} · {format_number(symbols)}\n")
                rank += 1
            f.write("\n")

            # Top invitees
            if invite_counts:
                f.write(f"{current_texts['invite_top']}:\n")
                sorted_invites = invite_counts.most_common()
                rank = 1
                for inviter, invite_count in sorted_invites:
                    inviter_id = user_ids.get(inviter, '')
                    if show_user_links:
                        user_link = f"tg://openmessage?user_id={inviter_id}" if inviter_id else ''
                        f.write(f"{rank}. {inviter} ({user_link}): {format_number(invite_count)} приглашений\n")
                    else:
                        f.write(f"{rank}. {inviter}: {format_number(invite_count)} приглашений\n")
                    rank +=1
                f.write("\n")

            # Title changes
            f.write(f"{current_texts['title_changes'].format(format_number(title_change_count))}\n\n")

        # Top words
        f.write(f"{config.emojis.get('word', '')} {current_texts.get('top_words', 'Top words')}:\n")
        rank = 1
        for word, freq in common_words:
            f.write(f"{rank}. {word}: {format_number(freq)} {current_texts.get('times', 'times')}\n")
            rank += 1
        f.write("\n")

        # Activity statistics
        f.write(f"{config.emojis.get('activity', '')} {current_texts.get('activity', 'Activity')}:\n")
        # Top hours
        hours_list = ', '.join([f"{config.emojis.get('list_item', '')} {hour}:00–{hour}:59" for hour, _ in activity['hours']])
        f.write(f"{hours_list}\n")
        # Top weekdays
        weekdays_list = ', '.join([f"{config.emojis.get('list_item', '')} {weekday}" for weekday, _ in activity['weekdays']])
        f.write(f"{weekdays_list}\n")
        # Top months
        months_list = ', '.join([f"{config.emojis.get('list_item', '')} {month.capitalize()}" for month, _ in activity['months']])
        f.write(f"{months_list}\n")
        # Top years
        years_list = ', '.join([f"{config.emojis.get('list_item', '')} {year}" for year, _ in activity['years']])
        f.write(f"{years_list}\n\n")

        # Most active days
        f.write(f"{config.emojis.get('activity', '')} {current_texts.get('most_active_days', 'Most active days')}:\n")
        rank = 1
        for date, msg_count in top_days:
            symbol_count = date_symbols[date]
            avg_length = symbol_count / msg_count if msg_count else 0
            date_str = date.strftime('%d.%m.%Y')
            f.write(f"{rank}. {date_str}: ✉️ {format_number(msg_count)}, 🔣 {format_number(symbol_count)}, 💬 {avg_length:.1f}\n")
            rank += 1
        f.write("\n")

        # Add group creator info
        if creator_name and creator_id:
            f.write(f"{current_texts['creator_info'].format(creator_name, creator_id)}\n")

        if show_author_links:
            f.write('\n\n')
            f.write('⚡️\n')
            f.write(current_texts['author_links'].format(author_github_link, author_telegram_channel))
            f.write('\n⚡️\n')

    # Save JSON output
    if save_json:
        json_output_filename = output_filename.replace('.txt', '.json')
        with open(json_output_filename, 'w', encoding='utf-8') as jf:
            json.dump(json_output_data, jf, ensure_ascii=False, indent=4)

    elapsed_time = time.time() - start_time
    print(current_texts['processing_completed'].format(elapsed_time, output_filename))

    if unprocessed_messages > 0:
        unprocessed_percentage = (unprocessed_messages / total_messages) * 100
        print(current_texts['unprocessed_messages'].format(unprocessed_percentage))
        print(current_texts['error_count'].format(error_count, error_log_filename))

    if config.show_author_links:
        print()
        print('⚡️')
        print(current_texts['author_links'].format(author_github_link, author_telegram_channel))
        print('⚡️')

def configure_in_console(config, current_texts):
    temp_config = {}
    print(current_texts['select_action'])
    # Example for 'exclude_bots'
    exclude_bots = input(f"Exclude bots? (y/n, default {config.exclude_bots}): ").strip().lower()
    temp_config['exclude_bots'] = False if exclude_bots == 'n' else True

    # 'show_non_consecutive_counts'
    show_non_consecutive_counts = input(f"Show non-consecutive message counts? (y/n, default {config.show_non_consecutive_counts}): ").strip().lower()
    temp_config['show_non_consecutive_counts'] = False if show_non_consecutive_counts == 'n' else True

    # 'top_participants_count'
    top_participants_count = input(f"Number of top participants to display (default {config.top_participants_count}): ").strip()
    temp_config['top_participants_count'] = int(top_participants_count) if top_participants_count.isdigit() else config.top_participants_count

    # 'top_words_count'
    top_words_count = input(f"Number of top words to display (default {config.top_words_count}): ").strip()
    temp_config['top_words_count'] = int(top_words_count) if top_words_count.isdigit() else config.top_words_count

    # 'show_user_links'
    show_user_links = input(f"Show user links? (y/n, default {config.show_user_links}): ").strip().lower()
    temp_config['show_user_links'] = False if show_user_links == 'n' else True

    return temp_config

def save_config_to_file(temp_config):
    with open('confignew.py', 'w', encoding='utf-8') as f:
        for key, value in temp_config.items():
            if isinstance(value, str):
                f.write(f"{key} = '{value}'\n")
            else:
                f.write(f"{key} = {value}\n")
    print("Настройки сохранены в confignew.py")

if __name__ == "__main__":
    main()