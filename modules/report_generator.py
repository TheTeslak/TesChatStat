# modules/report_generator.py

def format_number(number):
    """Format number with spaces as thousands separators."""
    s = str(int(number))
    return ' '.join([s[max(i - 3, 0):i] for i in range(len(s), 0, -3)][::-1])

def generate_text_report(analysis_results, config, current_texts, output_filename, author_github_link, author_telegram_channel, is_personal_chat):
    """Generate the textual report based on analysis results."""
    with open(output_filename, 'w', encoding='utf-8') as f:
        first_date = analysis_results['first_date']
        last_date = analysis_results['last_date']
        date_range_str = ''
        if first_date and last_date:
            date_range_str = f"за период: {first_date.strftime('%d.%m.%Y')} – {last_date.strftime('%d.%m.%Y')}"

        chat_name = analysis_results.get('chat_name', 'Chat Name')
        f.write(f"Статистика чата \"{chat_name}\" {date_range_str}\n\n")

        # Messages and symbols statistics
        total_msgs_formatted = format_number(analysis_results['total_messages'])
        total_symbols_formatted = format_number(analysis_results['total_symbols'])
        avg_message_length = analysis_results['avg_message_length']

        show_non_consecutive = config.get('show_non_consecutive_counts', True)
        if show_non_consecutive:
            total_non_consecutive_msgs_formatted = format_number(analysis_results['total_non_consecutive_messages'])
            total_non_consecutive_symbols_formatted = format_number(analysis_results['total_non_consecutive_symbols'])
            f.write(f"{config['emojis'].get('messages','')} {current_texts['messages'].capitalize()}: {total_msgs_formatted} ({total_non_consecutive_msgs_formatted} {current_texts.get('non_consecutive', 'not consecutive')})\n")
            f.write(f"{config['emojis'].get('symbols','')} {current_texts.get('symbols', 'symbols').capitalize()}: {total_symbols_formatted} ({total_non_consecutive_symbols_formatted} {current_texts.get('non_consecutive', 'not consecutive')})\n")
        else:
            f.write(f"{config['emojis'].get('messages','')} {current_texts['messages'].capitalize()}: {total_msgs_formatted}\n")
            f.write(f"{config['emojis'].get('symbols','')} {current_texts.get('symbols', 'symbols').capitalize()}: {total_symbols_formatted}\n")

        f.write(f"{config['emojis'].get('avg_symbols','')} {current_texts.get('avg_symbols_in_message', 'Symbols per message')}: {avg_message_length:.0f}\n\n")

        # Message counts by type
        message_counts = analysis_results['message_counts']
        f.write(f"{config['emojis'].get('pictures','')} {current_texts.get('pictures', 'Pictures')}: {format_number(message_counts['picture'])}\n")
        f.write(f"{config['emojis'].get('videos','')} {current_texts.get('videos', 'Videos')}: {format_number(message_counts['video'])}\n")
        f.write(f"{config['emojis'].get('files','')} {current_texts.get('files', 'Files')}: {format_number(message_counts['file'])}\n")
        f.write(f"{config['emojis'].get('audios','')} {current_texts.get('audios', 'Audios')}: {format_number(message_counts['audio'])}\n")
        f.write(f"{config['emojis'].get('links','')} {current_texts.get('links', 'Links')}: {format_number(message_counts['links'])}\n")
        f.write(f"{config['emojis'].get('voice','')} {current_texts.get('voice_messages', 'Voice messages')}: {format_number(message_counts['voice_message'])}\n")
        f.write(f"{config['emojis'].get('gif','')} GIF: {format_number(message_counts['gif'])}\n")
        f.write(f"{config['emojis'].get('sticker','')} {current_texts.get('stickers', 'Stickers')}: {format_number(message_counts['sticker'])}\n")
        f.write(f"{config['emojis'].get('emoji','')} {current_texts.get('emojis', 'Emoji')}: {format_number(message_counts['emojis'])}\n")
        f.write(f"{config['emojis'].get('poll','')} {current_texts.get('polls', 'Polls')}: {format_number(message_counts['poll'])}\n")
        f.write(f"{config['emojis'].get('command','')} {current_texts.get('commands', 'Commands')}: {format_number(message_counts['commands'])}\n")
        f.write(f"{config['emojis'].get('profanity','')} {current_texts.get('profanity_messages', 'Messages with profanity')}: {format_number(message_counts['profanity'])}\n\n")

        if is_personal_chat:
            # Personal chat statistics
            participants = list(analysis_results['user_counts'].keys())
            if len(participants) == 2:
                user_counts = analysis_results['user_counts']
                non_consecutive_counts = analysis_results['non_consecutive_counts']
                user1, user2 = participants
                count1 = user_counts[user1]
                count2 = user_counts[user2]
                non_consec_count1 = non_consecutive_counts[user1]
                non_consec_count2 = non_consecutive_counts[user2]

                f.write(f"{current_texts['personal_chat_stats'].format(user1, format_number(count1), format_number(non_consec_count1), user2, format_number(count2), format_number(non_consec_count2))}\n")

                # Estimate reading time
                total_symbols = analysis_results['total_symbols']
                total_reading_seconds = (total_symbols / 1000) * 60  # Assuming 1000 chars per minute
                total_reading_minutes = total_reading_seconds / 60
                total_reading_hours = total_reading_minutes / 60
                total_reading_days = total_reading_hours / 24
                total_reading_days_formatted = f"{total_reading_days:.2f}" if total_reading_days >= 1 else ""
                days_part = current_texts['days'].format(total_reading_days_formatted) if total_reading_days_formatted else ""
                f.write(f"\n{current_texts['reading_time_estimate'].format(int(total_reading_seconds), int(total_reading_minutes), int(total_reading_hours), days_part)}\n")
            else:
                f.write("Unexpected number of participants in personal chat.\n")
        else:
            # Top participants
            f.write(f"{config['emojis'].get('participant', '')} {current_texts.get('top_participants', 'Top participants')}:\n")
            sorted_users = analysis_results['user_counts'].most_common(config.get('top_participants_count'))
            rank = 1
            for user, count in sorted_users:
                non_consecutive_count = analysis_results['non_consecutive_counts'][user]
                symbols = analysis_results['user_symbols'][user]
                non_consecutive_symbols = analysis_results['non_consecutive_symbols'][user]
                user_id = analysis_results['user_ids'].get(user, '')
                if config.get('show_non_consecutive_counts', True):
                    if config.get('show_user_links', False):
                        user_link = f"tg://openmessage?user_id={user_id}" if user_id else ''
                        f.write(f"{rank}. {user} ({user_link}): {format_number(count)} ({format_number(non_consecutive_count)}) · {format_number(symbols)} ({format_number(non_consecutive_symbols)})\n")
                    else:
                        f.write(f"{rank}. {user}: {format_number(count)} ({format_number(non_consecutive_count)}) · {format_number(symbols)} ({format_number(non_consecutive_symbols)})\n")
                else:
                    if config.get('show_user_links', False):
                        user_link = f"tg://openmessage?user_id={user_id}" if user_id else ''
                        f.write(f"{rank}. {user} ({user_link}): {format_number(count)} · {format_number(symbols)}\n")
                    else:
                        f.write(f"{rank}. {user}: {format_number(count)} · {format_number(symbols)}\n")
                rank += 1
            f.write("\n")

            # Top inviters
            invite_counts = analysis_results['invite_counts']
            if invite_counts:
                f.write(f"{current_texts['invite_top']}:\n")
                sorted_invites = invite_counts.most_common()
                rank = 1
                for inviter, invite_count in sorted_invites:
                    inviter_id = analysis_results['user_ids'].get(inviter, '')
                    if config.get('show_user_links', False):
                        user_link = f"tg://openmessage?user_id={inviter_id}" if inviter_id else ''
                        f.write(f"{rank}. {inviter} ({user_link}): {format_number(invite_count)} приглашений\n")
                    else:
                        f.write(f"{rank}. {inviter}: {format_number(invite_count)} приглашений\n")
                    rank +=1
                f.write("\n")

            # Removed title changes from the report as per request

        # Top words
        common_words = analysis_results['common_words']
        f.write(f"{config['emojis'].get('word', '')} {current_texts.get('top_words', 'Top words')}:\n")
        rank = 1
        for word, freq in common_words:
            f.write(f"{rank}. {word}: {format_number(freq)} {current_texts.get('times', 'times')}\n")
            rank += 1
        f.write("\n")

        # Top phrases
        common_phrases = analysis_results['common_phrases']
        f.write(f"{config['emojis'].get('phrase', '')} {current_texts.get('top_phrases', 'Top phrases')}:\n")
        rank = 1
        for phrase, freq in common_phrases:
            f.write(f"{rank}. {phrase}: {format_number(freq)} {current_texts.get('times', 'times')}\n")
            rank += 1
        f.write("\n")

        # Activity statistics
        f.write(f"{config['emojis'].get('activity', '')} {current_texts.get('activity', 'Activity')}:\n")
        activity = analysis_results['activity']
        # Top hours
        hours_list = ', '.join([f"{config['emojis'].get('list_item', '')} {hour}:00–{hour}:59" for hour, _ in activity['hours']])
        f.write(f"{hours_list}\n")
        # Top weekdays
        weekdays_list = ', '.join([f"{config['emojis'].get('list_item', '')} {weekday}" for weekday, _ in activity['weekdays']])
        f.write(f"{weekdays_list}\n")
        # Top months
        months_list = ', '.join([f"{config['emojis'].get('list_item', '')} {month.capitalize()}" for month, _ in activity['months']])
        f.write(f"{months_list}\n")
        # Top years
        years_list = ', '.join([f"{config['emojis'].get('list_item', '')} {year}" for year, _ in activity['years']])
        f.write(f"{years_list}\n\n")

        # Most active days
        f.write(f"{config['emojis'].get('activity', '')} {current_texts.get('most_active_days', 'Most active days')}:\n")
        rank = 1
        date_symbols = analysis_results['date_symbols']
        for date, msg_count in analysis_results['top_days']:
            symbol_count = date_symbols[date]
            avg_length = symbol_count / msg_count if msg_count else 0
            date_str = date.strftime('%d.%m.%Y')
            f.write(f"{rank}. {date_str}: ✉️ {format_number(msg_count)}, 🔣 {format_number(symbol_count)}, 💬 {avg_length:.1f}\n")
            rank += 1
        f.write("\n")

        # Add group creator info
        if analysis_results['creator_name'] and analysis_results['creator_id']:
            f.write(f"{current_texts['creator_info'].format(analysis_results['creator_name'], analysis_results['creator_id'])}\n")

        if config.get('show_author_links', True):
            f.write('\n\n')
            f.write('⚡️\n')
            f.write(current_texts['author_links'].format(author_github_link, author_telegram_channel))
            f.write('\n⚡️\n')

def generate_json_report(analysis_results, json_output_filename):
    """Generate the JSON report (currently empty)."""
    json_output_data = {
        # Include any data you want to output to the JSON file
    }
    with open(json_output_filename, 'w', encoding='utf-8') as jf:
        json.dump(json_output_data, jf, ensure_ascii=False, indent=4)