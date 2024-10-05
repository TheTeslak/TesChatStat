# modules/data_loader.py

import json
import os
import re
import ijson

def load_json_file_streaming(input_file, header_only=False):
    """Load JSON data using streaming parsing."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            parser = ijson.parse(f)
            data = {}
            current_key = None
            for prefix, event, value in parser:
                if prefix == '' and event == 'map_key':
                    current_key = value
                elif current_key == 'name' and prefix == 'name' and event == 'string':
                    data['name'] = value
                elif current_key == 'type' and prefix == 'type' and event == 'string':
                    data['type'] = value
                elif current_key == 'id' and prefix == 'id' and event in ('number', 'string'):
                    data['id'] = value
                elif current_key == 'messages' and event == 'start_array':
                    if header_only:
                        break
                    else:
                        data['messages'] = []
                        for msg in ijson.items(f, 'messages.item'):
                            data['messages'].append(msg)
                    break  # We have everything we need
            return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

def merge_json_files(folder_path, output_file, current_texts):
    """Merge multiple JSON files matching a pattern into a single output file."""
    merged_messages = {}
    pattern = re.compile(r'^result\d*\.json$')  # Modified to match 'result.json' and 'resultNUMBER.json'
    header_data = None
    if not os.path.isdir(folder_path) or folder_path == '':
        folder_path = '.'  # Use current directory if folder is not specified or does not exist

    files_found = False
    for filename in os.listdir(folder_path):
        if pattern.match(filename):
            files_found = True
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                print(f"Processing file: {file_path}")
                data = load_json_file_streaming(file_path)
                if data:
                    # Use header data from the first file
                    if header_data is None:
                        header_data = {k: data[k] for k in data if k != 'messages'}
                    # Merge messages
                    for message in data.get('messages', []):
                        message_id = message.get('id')
                        if message_id is not None:
                            # If the message_id is new or we prefer to replace existing messages
                            merged_messages[message_id] = message
    if not files_found:
        print(f"No files matching 'result*.json' pattern found in '{folder_path}'.")
        return

    # Sort messages by 'id'
    sorted_messages = sorted(merged_messages.values(), key=lambda x: x.get('id'))

    # Update header_data with merged messages
    if header_data:
        header_data['messages'] = sorted_messages
        # Save the merged data to the output file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(header_data, f, ensure_ascii=False)
            print(f"✅ Files have been merged into '{output_file}'.")
        except Exception as e:
            print(f"❌ Error writing merged file: {e}")
    else:
        print("❌ No header data found. Cannot save merged file.")