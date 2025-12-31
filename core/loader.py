import os
import ijson
import glob
import re
import heapq
from typing import Generator, Dict, Optional, Tuple, List

def autodetect_input_file(default_file: str, excluded_files: list = None) -> Tuple[List[str], str]:
    """
    Intelligently finds input JSON files.
    Detects split archives (result.json, result2.json...) automatically.
    
    Returns: ([list_of_files], status_message_key)
    """
    if excluded_files is None:
        excluded_files = ['settings.json', 'package.json']

                               
    if os.path.exists(default_file):
        return _expand_split_files(default_file), 'found-default'

                                    
    candidates = []
    for f in glob.glob("*.json"):
        if f not in excluded_files and not f.startswith('report') and not f.startswith('data'):
            candidates.append(f)

                        
    if not candidates:
        return [], 'err-no-files'
    
                                                                                
    if 'result.json' in candidates:
        return _expand_split_files('result.json'), 'found-auto'
        
    if len(candidates) == 1:
        return [candidates[0]], 'found-auto'
    
    return [], 'err-ambiguous-files'

def _expand_split_files(base_file: str) -> List[str]:
    """
    Looks for sibling files with numeric suffixes regardless of the filename.
    Example: if base is 'chat.json', finds 'chat2.json', 'chat3.json'.
    """
    directory = os.path.dirname(base_file) or "."
    filename = os.path.basename(base_file)
    
                                                                   
    name_no_ext, ext = os.path.splitext(filename)
    
                                                                        
    base_prefix = re.sub(r'\d+$', '', name_no_ext)
    
                                          
    search_pattern = os.path.join(directory, f"{base_prefix}*{ext}")
    candidates = glob.glob(search_pattern)
    
    sequence = []
                                                          
    match_pattern = re.compile(rf'^{re.escape(base_prefix)}(\d*){re.escape(ext)}$')
    
    for path in candidates:
        f_name = os.path.basename(path)
        match = match_pattern.match(f_name)
        if match:
            num_str = match.group(1)
                                                   
                                                 
            idx = 1 if num_str == '' else int(num_str)
            sequence.append((idx, path))
            
                                                
    sequence.sort(key=lambda x: x[0])
    
    return [path for _, path in sequence]

def detect_json_structure(file_path: str) -> str:
    """
    'Sniffer' - reads the first few JSON events to determine structure.
    Uses ijson parser (lazy) to avoid reading the whole file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            parser = ijson.parse(f)
            count = 0
            for prefix, event, value in parser:
                count += 1
                if count > 50: break
                
                if prefix == '' and event == 'map_key' and value == 'messages':
                    return 'messages.item'
                if prefix == '' and event == 'map_key' and value == 'history':
                    return 'history.item'
                if prefix == '' and event == 'start_array':
                    return 'item'
    except (ijson.JSONError, UnicodeDecodeError, FileNotFoundError):
        pass
    return 'messages.item'

def load_json_header(file_path: str) -> Optional[Dict]:
    """Reads metadata (name, type, id) from the first file's root."""
    header_fields = {'name', 'type', 'id'}
    header_data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            parser = ijson.parse(f)
            current_key = None
            for prefix, event, value in parser:
                if prefix == '' and event == 'map_key':
                    current_key = value
                elif current_key in header_fields and event in ('string', 'number', 'integer'):
                    header_data[current_key] = value
                if len(header_data) == len(header_fields): break
                if current_key in ('messages', 'history'): break
    except (FileNotFoundError, ijson.JSONError):
        pass
    return header_data if header_data else None

def stream_messages(file_paths: List[str], buffer_size=300) -> Generator[Dict, None, None]:
    """
    Yields messages from multiple files sequentially using a Min-Heap Jitter Buffer.
    
    Features:
    - O(log N) insertion and removal via heapq.
    - Uses a `tie_breaker` counter to maintain input order for messages within same second.
    - Corrects chronological errors on file boundaries (e.g., result.json end vs result2.json start).
    """
    if not file_paths:
        return

    path_selector = detect_json_structure(file_paths[0])
    
                                                            
                                                                                           
    heap_buffer = []
    tie_breaker = 0
    
    for fp in file_paths:
        if not os.path.exists(fp):
            continue
            
        with open(fp, 'r', encoding='utf-8') as f:
            try:
                raw_stream = ijson.items(f, path_selector)
                
                for msg in raw_stream:
                    try:
                        ts = int(msg.get('date_unixtime', 0))
                    except (ValueError, TypeError):
                        ts = 0
                        
                                            
                    heapq.heappush(heap_buffer, (ts, tie_breaker, msg))
                    tie_breaker += 1
                    
                                                           
                    if len(heap_buffer) >= buffer_size:
                        yield heapq.heappop(heap_buffer)[2]
                        
            except (ijson.JSONError, StopIteration):
                pass

                                          
    while heap_buffer:
        yield heapq.heappop(heap_buffer)[2]