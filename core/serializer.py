import json
import dataclasses
from datetime import datetime, date
from typing import Tuple, Optional, Any
import config

class AnalyzeEncoder(json.JSONEncoder):
    """
    Standard JSON Encoder for primitive types not handled by recursive dict conversion.
    """
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)
        return super().default(o)

def _recursive_stringify_keys(obj: Any) -> Any:
    """
    Recursively traverses dictionaries and converts tuple/mixed keys to strings.
    Ensures compatibility with JSON standard (keys must be strings).
    """
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
                                                                             
            if isinstance(k, (tuple, list)):
                key_str = "-".join(map(str, k))
            else:
                key_str = str(k)
            new_dict[key_str] = _recursive_stringify_keys(v)
        return new_dict
    elif isinstance(obj, list):
        return [_recursive_stringify_keys(i) for i in obj]
    return obj

def save_result_to_json(result_obj, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Saves analysis result to JSON with Deep Copy protection.
    Uses dataclasses.asdict() to generate a clean dictionary structure,
    then normalizes all keys and prunes unnecessary data.
    """
    try:
                                      
                                                                            
                                                                                 
        raw_data = dataclasses.asdict(result_obj)
        
                                                 
        if not config.FULL_JSON_EXPORT:
            keys_to_remove = [
                'days_activity', 
                'daily_first_senders', 
                'heatmap_data', 
                'daily_user_activity'
            ]
            for key in keys_to_remove:
                if key in raw_data:
                    del raw_data[key]
            
                                                   
            if 'users_activity' in raw_data:
                for user_act in raw_data['users_activity'].values():
                    if 'active_days' in user_act:
                        user_act['active_days'] = []

                                           
                                                                                 
                                      
        clean_data = _recursive_stringify_keys(raw_data)

                              
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, cls=AnalyzeEncoder, ensure_ascii=False, indent=2)
            
        return True, None
    except Exception as e:
        return False, str(e)