# modules/data_loader.py

import json
import os
import re

def load_json_file(input_file):
    """Load JSON data from the given file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def merge_json_files(folder_path, output_file, current_texts):
    """Merge multiple JSON files matching a pattern into a single output file."""
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
        print(f"✅ Files matching 'result*.json' pattern in '{folder_path}' have been merged into '{output_file}'.")
    else:
        print("❌ No data found to merge.")