# modules/analyzer.py

import datetime
from collections import Counter, defaultdict
import re

def is_bot(user_name, bot_identifiers):
    """Check if the user is a bot based on identifiers."""
    return any(bot_id.lower() in user_name.lower() for bot_id in bot_identifiers)

def format_number(number):
    """Format number with spaces as thousands separators."""
    s = str(int(number))
    return ' '.join([s[max(i - 3, 0):i] for i in range(len(s), 0, -3)][::-1])

def analyze_messages(data, config, current_texts, is_personal_chat):
    """Analyze messages and collect statistics."""
    messages = data.get('messages', [])
    total_messages = len(messages)
    total_messages_formatted = format_number(total_messages)
    print(current_texts['total_messages'].format(total_messages_formatted))

    if total_messages == 0:
        return {}, {'errors': [], 'unprocessed_messages': 0}

    # Store chat name from data
    chat_name = data.get('name', 'Chat Name')

    # Initialize variables for analysis
    user_counts = Counter()
    user_symbols = Counter()
    non_consecutive_counts = Counter()
    user_ids = {}
    prev_user = None
    prev_time = None
    words = []
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
    # For tracking invitations
    invite_counts = Counter()
    title_change_count = 0
    creator_name = None
    creator_id = None
    includes_media = 0  # For estimating reading time
    chain_started = False  # For non-consecutive message counting

    # Extract configurations and patterns
    profanity_words = set(config.get('profanity_words', []))
    commands_identifiers = set(config.get('commands_identifiers', ['/']))
    emoji_pattern = config['emoji_pattern']
    url_pattern = config['url_pattern']
    stop_words = set(config.get('stop_words', []))
    stop_words.update({'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you',
                       'that', 'he', 'was', 'for', 'on', 'are', 'with', 'as', 'i',
                       'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from'})

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

    total_messages = len(messages)
    spinner = ['|', '/', '-', '\\']
    spinner_index = 0

    def print_progress(current, total):
        """Print the progress of message processing."""
        nonlocal spinner_index
        current_formatted = format_number(current)
        total_formatted = format_number(total)
        progress = current_texts['processing'].format(current_formatted, total_formatted, spinner[spinner_index % len(spinner)])
        spinner_index += 1
        print(progress, end='\r', flush=True)

    for idx, message in enumerate(messages):
        try:
            # Skip messages without 'from' or 'actor'
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
            if not is_personal_chat and config.get('exclude_bots', True) and is_bot(user, config.get('bot_identifiers', [])):
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
                user_counts[user] += 1
                user_symbols[user] += symbols

                if prev_user != user:
                    non_consecutive_counts[user] += 1
                    chain_started = True
                else:
                    chain_started = False

                # Process message date and time
                message_date = message.get('date')
                if message_date:
                    try:
                        date_time = datetime.datetime.fromisoformat(message_date)
                        if first_date is None or date_time < first_date:
                            first_date = date_time
                        if last_date is None or date_time > last_date:
                            last_date = date_time

                        # For personal chat, track daily message counts and first sender
                        if is_personal_chat:
                            date_only = date_time.date()
                            daily_user_messages[date_only][user] += 1
                            if date_only not in daily_first_sender:
                                daily_first_sender[date_only] = user

                            # Track intervals of inactivity greater than 1 hour
                            if prev_time:
                                delta = date_time - prev_time
                                if delta.total_seconds() > 3600:
                                    # Optionally store intervals
                                    pass
                            prev_time = date_time

                        hours[date_time.hour] += 1
                        weekday_index = date_time.weekday()
                        weekday_name = config['day_names']['ru'][weekday_index]
                        weekdays[weekday_name] += 1
                        month_name = f"{config['month_names']['ru'][date_time.month -1]} {date_time.year}"
                        months[month_name] +=1
                        years[date_time.year] +=1
                        date_only = date_time.date()
                        dates[date_only] += 1
                        date_messages[date_only] += 1
                        date_symbols[date_only] += symbols
                    except (ValueError, KeyError) as e:
                        error_count +=1
                        errors.append(f"Error processing date in message id {message.get('id')}: {e}\n")
                else:
                    prev_time = None

                prev_user = user

                # Collect words for frequency analysis
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
                    # Check for media in messages without 'media_type' field
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
                # Handle service messages
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
            errors.append(f"Error processing message id {msg_id}: {e}\n")

    print_progress(total_messages, total_messages)
    print('\n')

    # Calculate statistics
    total_msgs = sum(user_counts.values())
    total_symbols = sum(user_symbols.values())
    avg_message_length = total_symbols / total_msgs if total_msgs else 0
    common_words = Counter(words).most_common(config.get('top_words_count', 100))
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
        'user_counts': user_counts,
        'user_symbols': user_symbols,
        'non_consecutive_counts': non_consecutive_counts,
        'user_ids': user_ids,
        'first_date': first_date,
        'last_date': last_date,
        'avg_message_length': avg_message_length,
        'common_words': common_words,
        'activity': activity,
        'top_days': top_days,
        'message_counts': message_counts,
        'invite_counts': invite_counts,
        'title_change_count': title_change_count,
        'creator_name': creator_name,
        'creator_id': creator_id,
        'date_symbols': date_symbols,
        'includes_media': includes_media,
        'dates': dates,
        'date_messages': date_messages,
        'daily_user_messages': daily_user_messages,
        'daily_first_sender': daily_first_sender,
    }

    error_info = {
        'errors': errors,
        'unprocessed_messages': unprocessed_messages,
    }

    return analysis_results, error_info