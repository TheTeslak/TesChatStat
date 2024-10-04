# modules/config_handler.py

def configure_in_console(config, current_texts, is_personal_chat):
    """Configure settings in the console, adjusting for chat type."""
    temp_config = {}
    print(current_texts['select_action'])

    # Common configurations
    top_words_count = input(f"Number of top words to display (default {config.top_words_count}): ").strip()
    temp_config['top_words_count'] = int(top_words_count) if top_words_count.isdigit() else config.top_words_count

    # Configurations specific to group chats
    if not is_personal_chat:
        exclude_bots = input(f"Exclude bots? (y/n, default {'Yes' if config.exclude_bots else 'No'}): ").strip().lower()
        temp_config['exclude_bots'] = exclude_bots != 'n'  # Default to True if empty or 'y'

        show_non_consecutive_counts = input(f"Show non-consecutive message counts? (y/n, default {'Yes' if config.show_non_consecutive_counts else 'No'}): ").strip().lower()
        temp_config['show_non_consecutive_counts'] = show_non_consecutive_counts != 'n'

        top_participants_count = input(f"Number of top participants to display (default {config.top_participants_count}): ").strip()
        temp_config['top_participants_count'] = int(top_participants_count) if top_participants_count.isdigit() else config.top_participants_count

        show_user_links = input(f"Show user links? (y/n, default {'Yes' if config.show_user_links else 'No'}): ").strip().lower()
        temp_config['show_user_links'] = show_user_links != 'n'
    else:
        # Configurations specific to personal chats
        pass  # Add any personal chat-specific configurations if needed

    # Copy other configurations
    temp_config['input_file'] = config.input_file
    temp_config['merge_folder'] = config.merge_folder
    temp_config['output_filename_pattern'] = config.output_filename_pattern
    temp_config['show_author_links'] = config.show_author_links
    temp_config['stop_words'] = config.stop_words
    temp_config['profanity_words'] = config.profanity_words
    temp_config['commands_identifiers'] = config.commands_identifiers
    temp_config['emoji_pattern'] = config.emoji_pattern
    temp_config['url_pattern'] = config.url_pattern
    temp_config['day_names'] = config.day_names
    temp_config['month_names'] = config.month_names
    temp_config['top_days_count'] = config.top_days_count
    temp_config['bot_identifiers'] = config.bot_identifiers
    temp_config['emojis'] = config.emojis

    return temp_config

def save_config_to_file(temp_config):
    """Save the temporary configuration to a new file."""
    with open('confignew.py', 'w', encoding='utf-8') as f:
        for key, value in temp_config.items():
            if isinstance(value, str):
                f.write(f"{key} = '{value}'\n")
            else:
                f.write(f"{key} = {value}\n")
    print("Settings have been saved to confignew.py")