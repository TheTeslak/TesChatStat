import json
import os
import config
from datetime import datetime
from typing import Dict, Any

SETTINGS_FILE = 'settings.json'

def load_settings():
    """
    Loads settings from settings.json and overrides defaults in config.py.
    Handles type conversion for special fields like Dates with explicit warnings.
    """
    if not os.path.exists(SETTINGS_FILE):
        return

    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            user_settings = json.load(f)
        
        for key, value in user_settings.items():
            if not hasattr(config, key):
                continue
            
                                        
            if key in ('START_DATE', 'END_DATE') and value:
                try:
                    dt = datetime.strptime(value, "%d.%m.%Y")
                    setattr(config, key, dt)
                except ValueError:
                    print(f"⚠️  Warning: Invalid date format for '{key}' in settings.json. Expected DD.MM.YYYY. Using default.")
                    continue 
            else:
                setattr(config, key, value)
                
    except json.JSONDecodeError as e:
        print(f"⚠️  Error: settings.json is malformed. {e}")
    except OSError as e:
        print(f"⚠️  Error loading settings: {e}")

def save_settings(new_settings: Dict[str, Any]) -> bool:
    """
    Saves a dictionary of settings to settings.json.
    Converts datetime objects to strings. Merges with existing settings to preserve comments/other keys.
    """
    final_data = {}
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                final_data = json.load(f)
        except:
            pass                                

    for k, v in new_settings.items():
        if isinstance(v, (datetime,)):
            final_data[k] = v.strftime("%d.%m.%Y")
        else:
            final_data[k] = v

    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"❌ Failed to save settings: {e}")
        return False