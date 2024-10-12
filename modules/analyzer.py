import datetime
from collections import Counter, defaultdict
import re
import os
import ijson
import json

def is_bot(user_name, bot_identifiers):
    """Check if the user is a bot based on identifiers."""
    return any(bot_id.lower() in user_name.lower() for bot_id in bot_identifiers)

def format_number(number):
    """Format number with spaces as thousands separators."""
    s = str(int(number))
    return ' '.join([s[max(i - 3, 0):i] for i in range(len(s), 0, -3)][::-1])

def load_word_list(file_path):
    """Load words from a file into a set."""
    words = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    words.add(word)
    return words

def analyze_messages(input_file, config, current_texts, is_personal_chat, use_streaming=False):
    """Analyze messages and collect statistics."""
    if use_streaming:
        # Use streaming JSON parsing
        messages = parse_messages_streaming(input_file)
        total_messages = 0  # Will be counted during processing
        header_data = load_json_header(input_file)
        chat_name = header_data.get('name', 'Chat Name')
    else:
        # Load entire JSON data
        data = load_json_file(input_file)
        messages = data.get('messages', [])
        total_messages = len(messages)
        print(current_texts['total_messages'].format(format_number(total_messages)))
        if total_messages == 0:
            return {}, {'errors': [], 'unprocessed_messages': 0}
        chat_name = data.get('name', 'Chat Name')

    # Initialize variables for analysis
    user_counts = Counter()
    user_symbols = Counter()
    non_consecutive_counts = Counter()
    non_consecutive_symbols = Counter()
    user_ids = {}
    prev_user = None
    prev_time = None
    words = []
    phrases_2 = []
    phrases_3 = []
    hours = Counter()
    weekdays = Counter()
    months = Counter()
    years = Counter()
    dates = Counter()
    date_messages = defaultdict(int)
    date_symbols = defaultdict(int)
    # For personal chat plots
    daily_user_messages = defaultdict(lambda: Counter())
    daily_first_sender = {}
    daily_user_non_consecutive_messages = defaultdict(lambda: Counter())
    # For tracking invitations
    invite_counts = Counter()
    # Removed title_change_count as per request
    creator_name = None
    creator_id = None
    includes_media = 0  # For estimating reading time
    chain_started = False  # For non-consecutive message counting

    # Load stop words and profanity words from files
    words_dir = config.get('words_dir', 'words')
    stop_words_type = config.get('stop_words_type', 'minimal')
    stop_words_file = os.path.join(words_dir, f'stop_words_{stop_words_type}.txt')
    profanity_words_file = os.path.join(words_dir, 'profanity_words.txt')

    # Load stop words
    stop_words = load_word_list(stop_words_file)

    # Load English stop words
    english_stop_words_file = os.path.join(words_dir, 'stop_words_english.txt')
    english_stop_words = load_word_list(english_stop_words_file)
    stop_words.update(english_stop_words)

    # Ensure default stop words if file not found
    if not stop_words:
        stop_words = set(['и', 'в', 'не', 'на', 'с', 'что', 'а', 'как', 'это', 'по', 'но',
                          'из', 'у', 'за', 'о', 'же', 'то', 'к', 'для', 'до', 'вы', 'мы',
                          'они', 'он', 'она', 'оно', 'так', 'было', 'только', 'бы', 'когда',
                          'уже', 'ли', 'или', 'со'])
        # Adding default English stop words
        default_english_stop_words = set(['a', 'the', 'and', 'or', 'but', 'if', 'in', 'on', 'with', 'for', 'is', 'was', 'are', 'were', 'be', 'to', 'of', 'at', 'by', 'an'])
        stop_words.update(default_english_stop_words)

    # Load profanity words
    profanity_words = load_word_list(profanity_words_file)

    # Other configurations and patterns
    commands_identifiers = set(config.get('commands_identifiers', ['/']))
    emoji_pattern = config['emoji_pattern']
    url_pattern = config['url_pattern']

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

    first_date = None
    last_date = None

    unprocessed_messages = 0
    error_count = 0
    errors = []

    spinner = ['|', '/', '-', '\\']
    spinner_index = 0

    def print_progress(current):
        nonlocal spinner_index
        current_formatted = format_number(current)
        progress = current_texts['processing'].format(current_formatted, 'Unknown', spinner[spinner_index % len(spinner)])
        spinner_index += 1
        print(progress, end='\r', flush=True)

    # Get the interval from config (default to 1 hour)
    first_message_interval_seconds = config.get('first_message_interval_hours', 1) * 3600

    time_offset = config.get('time_offset', 0)  # Time offset in hours
    time_offset_delta = datetime.timedelta(hours=time_offset)

    total_messages_processed = 0

    for message in messages:
        total_messages_processed += 1

        user = None  # Initialize user as None

        if message is None or message.get('type') != 'message':
            prev_user = None
            continue

        try:
            # Ensure the 'text' field is present
            if 'text' not in message:
                prev_user = None
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
            if not is_personal_chat and config.get('exclude_bots', True) and is_bot(user, config.get('bot_identifiers', [])):
                prev_user = user  # Update prev_user before continuing
                continue

            # Process the 'text' field
            text = message['text']
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

            # Calculate symbols and update counts
            symbols = len(text)
            user_counts[user] += 1
            user_symbols[user] += symbols

            if prev_user != user:
                non_consecutive_counts[user] += 1
                non_consecutive_symbols[user] += symbols
                chain_started = True
            else:
                chain_started = False

            # Process message date and time
            message_date = message.get('date')
            if message_date:
                try:
                    date_time = datetime.datetime.fromisoformat(message_date)
                    # Apply time offset
                    date_time += time_offset_delta
                    if first_date is None or date_time < first_date:
                        first_date = date_time
                    if last_date is None or date_time > last_date:
                        last_date = date_time

                    date_only = date_time.date()

                    if is_personal_chat:
                        # For personal chat plots
                        daily_user_messages[date_only][user] += 1
                        if prev_user != user:
                            daily_user_non_consecutive_messages[date_only][user] += 1

                        # Track daily first sender
                        if date_only not in daily_first_sender or (prev_time and (date_time - prev_time).total_seconds() > first_message_interval_seconds):
                            daily_first_sender[date_only] = user

                    # For group chats and overall stats
                    date_messages[date_only] +=1
                    date_symbols[date_only] += symbols

                    hours[date_time.hour] += 1
                    weekday_index = date_time.weekday()
                    weekday_name = config['day_names']['ru'][weekday_index]
                    weekdays[weekday_name] += 1
                    month_name = f"{config['month_names']['ru'][date_time.month -1]} {date_time.year}"
                    months[month_name] +=1
                    years[date_time.year] +=1
                    dates[date_only] += 1
                except (ValueError, KeyError) as e:
                    error_count +=1
                    errors.append(f"Error processing date in message id {message.get('id')}: {e}\n")
            else:
                prev_time = None

            prev_user = user
            if 'date_time' in locals():
                prev_time = date_time

            # Collect words for frequency analysis
            if text:
                text_clean = re.sub(r'[^\w\s]', '', text.lower())
                words_in_text = [word for word in text_clean.split() if word.isalpha()]

                # Collect phrases (2- and 3-word sequences)
                words_filtered = [word for word in words_in_text if word not in stop_words]
                for i in range(len(words_filtered) - 1):
                    phrase_2 = f"{words_filtered[i]} {words_filtered[i+1]}"
                    phrases_2.append(phrase_2)
                    if i < len(words_filtered) - 2:
                        phrase_3 = f"{words_filtered[i]} {words_filtered[i+1]} {words_filtered[i+2]}"
                        phrases_3.append(phrase_3)

                # Add to words list
                words.extend([word for word in words_in_text if word not in stop_words])

                # Check for commands
                if text.strip().startswith(tuple(commands_identifiers)):
                    message_counts['commands'] += 1

                # Check for emojis
                if emoji_pattern.search(text):
                    message_counts['emojis'] += 1

                # Check for profanity
                text_lower = text.lower()
                if any(phrase in text_lower for phrase in profanity_words):
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
                    if mime_type and mime_type.startswith('image/'):
                        message_counts['picture'] += 1
                    else:
                        message_counts['file'] += 1
                    includes_media += 1
                elif media_type == 'animation':
                    message_counts['gif'] +=1
                    includes_media += 1
                elif media_type == 'poll':
                    message_counts['poll'] += 1
                else:
                    # Handle other media types if needed
                    includes_media += 1
            else:
                # Check for media in messages without 'media_type' field
                if 'photo' in message:
                    message_counts['picture'] += 1
                    includes_media += 1
                elif 'file' in message:
                    mime_type = message.get('mime_type', '')
                    if mime_type and mime_type.startswith('image/'):
                        message_counts['picture'] += 1
                    else:
                        message_counts['file'] += 1
                    includes_media += 1
                else:
                    message_counts['text'] += 1

        except Exception as e:
            unprocessed_messages += 1
            error_count += 1
            msg_id = message.get('id', 'Unknown') if isinstance(message, dict) else 'Unknown'
            errors.append(f"Error processing message id {msg_id}: {e}\n")
            prev_user = None
            continue

        # Ensure prev_user is updated at the end of each iteration
        prev_user = user

        # Update progress
        if total_messages_processed % 1000 == 0:
            print_progress(total_messages_processed)

    # Final progress update
    print_progress(total_messages_processed)
    print('\n')

    total_messages = total_messages_processed  # Total messages processed
    print(current_texts['total_messages'].format(format_number(total_messages)))

    # Calculate statistics
    total_msgs = sum(user_counts.values())
    total_symbols = sum(user_symbols.values())
    total_non_consecutive_msgs = sum(non_consecutive_counts.values())
    total_non_consecutive_symbols = sum(non_consecutive_symbols.values())
    avg_message_length = total_symbols / total_msgs if total_msgs else 0
    common_words = Counter(words).most_common(config.get('top_words_count', 100))
    common_phrases = Counter(phrases_2 + phrases_3).most_common(config.get('top_phrases_count', 100))
    activity = {
        'hours': hours.most_common(3) if hours else [],
        'weekdays': weekdays.most_common(3) if weekdays else [],
        'months': months.most_common(3) if months else [],
        'years': years.most_common(3) if years else [],
    }
    # Top most active days
    top_days = dates.most_common(config.get('top_days_count', 10))

    analysis_results = {
        'chat_name': chat_name,
        'total_messages': total_msgs,
        'total_symbols': total_symbols,
        'total_non_consecutive_messages': total_non_consecutive_msgs,
        'total_non_consecutive_symbols': total_non_consecutive_symbols,
        'user_counts': user_counts,
        'user_symbols': user_symbols,
        'non_consecutive_counts': non_consecutive_counts,
        'non_consecutive_symbols': non_consecutive_symbols,
        'user_ids': user_ids,
        'first_date': first_date,
        'last_date': last_date,
        'avg_message_length': avg_message_length,
        'common_words': common_words,
        'common_phrases': common_phrases,
        'activity': activity,
        'top_days': top_days,
        'message_counts': message_counts,
        'invite_counts': invite_counts,
        'creator_name': creator_name,
        'creator_id': creator_id,
        'date_symbols': date_symbols,
        'includes_media': includes_media,
        'dates': dates,
        'date_messages': date_messages,
        'daily_user_messages': daily_user_messages,
        'daily_first_sender': daily_first_sender,
        'daily_user_non_consecutive_messages': daily_user_non_consecutive_messages,
    }

    error_info = {
        'errors': errors,
        'unprocessed_messages': unprocessed_messages,
    }

    return analysis_results, error_info

def parse_messages_streaming(input_file):
    """Parse messages from JSON file using streaming parsing."""
    with open(input_file, 'r', encoding='utf-8') as f:
        messages = ijson.items(f, 'messages.item')
        for message in messages:
            if message is not None:
                yield message

def load_json_header(input_file):
    """Load only the header information from the JSON file."""
    header_fields = ['name', 'type', 'id']
    header_data = {}
    with open(input_file, 'r', encoding='utf-8') as f:
        parser = ijson.parse(f)
        current_field = None
        for prefix, event, value in parser:
            if prefix == '' and event == 'map_key':
                current_field = value
            elif current_field in header_fields and event in ('string', 'number'):
                header_data[current_field] = value
            if all(field in header_data for field in header_fields):
                break  # Stop parsing after collecting all header fields
    return header_data

def load_json_file(input_file):
    """Load the entire JSON file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data