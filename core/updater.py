import requests
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from .constants import APP_VERSION, GITHUB_VERSION_URL, GITHUB_REPO_URL
from .i18n import t

SUPPORTED_SCHEMA_VERSION = 1

class UpdateStatusType(Enum):
    UP_TO_DATE = auto()
    UPDATE_FOUND = auto()
    OBSOLETE_SCHEMA = auto()
    ALERT_ONLY = auto()
    FAIL = auto()

@dataclass
class UpdateEntry:
    version: str
    date: str
    importance: str
    tags: List[str]
    description: str
    req_pip: bool
    req_config: bool

@dataclass
class RemoteStatus:
    status_type: UpdateStatusType
    latest_version: str = "0.0.0"
    alert_message: Optional[str] = None
    download_url: str = GITHUB_REPO_URL
    changelog: List[UpdateEntry] = field(default_factory=list)
    error_details: Optional[str] = None

def _parse_version(v_str: str) -> tuple:
    try:
        clean = "".join([c for c in v_str if c.isdigit() or c == '.'])
        return tuple(map(int, clean.split('.')))
    except ValueError:
        return (0, 0, 0)

def check_for_updates(current_lang: str = 'en') -> RemoteStatus:
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=3)
        if response.status_code != 200:
            return RemoteStatus(status_type=UpdateStatusType.FAIL, error_details=f"HTTP {response.status_code}")
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            return RemoteStatus(status_type=UpdateStatusType.FAIL, error_details="Invalid JSON")

        remote_schema = data.get('schema_version', 0)
        if remote_schema > SUPPORTED_SCHEMA_VERSION:
            return RemoteStatus(status_type=UpdateStatusType.OBSOLETE_SCHEMA, download_url=data.get('links', {}).get('download', GITHUB_REPO_URL))
        
        if remote_schema < 1:
             return RemoteStatus(status_type=UpdateStatusType.FAIL, error_details="Bad Schema")

        remote_ver_str = data.get('latest_version', '0.0.0')
        local_ver_tuple = _parse_version(APP_VERSION)
        remote_ver_tuple = _parse_version(remote_ver_str)
        
        has_update = remote_ver_tuple > local_ver_tuple
        
        alert_msg = None
        alert_data = data.get('alerts', {})
        if alert_data and alert_data.get('message'):
            msg_raw = alert_data.get('message')
            if isinstance(msg_raw, dict):
                alert_msg = msg_raw.get(current_lang, msg_raw.get('en'))
            else:
                alert_msg = str(msg_raw)

        changelog = []
        if has_update:
            history = data.get('history', [])
            for item in history:
                item_ver_str = item.get('v', '0.0.0')
                if _parse_version(item_ver_str) > local_ver_tuple:
                    desc_map = item.get('desc', {})
                    description = desc_map.get(current_lang, desc_map.get('en', ''))
                    reqs = item.get('requirements', {})
                    entry = UpdateEntry(
                        version=item_ver_str,
                        date=item.get('date', ''),
                        importance=item.get('importance', 'low'),
                        tags=item.get('tags', []),
                        description=description,
                        req_pip=reqs.get('pip_update', False),
                        req_config=reqs.get('config_reset', False)
                    )
                    changelog.append(entry)

        if has_update: st = UpdateStatusType.UPDATE_FOUND
        elif alert_msg: st = UpdateStatusType.ALERT_ONLY
        else: st = UpdateStatusType.UP_TO_DATE

        return RemoteStatus(status_type=st, latest_version=remote_ver_str, alert_message=alert_msg, download_url=data.get('links', {}).get('download', GITHUB_REPO_URL), changelog=changelog)

    except requests.exceptions.RequestException:
        return RemoteStatus(status_type=UpdateStatusType.UP_TO_DATE)
    except Exception as e:
        return RemoteStatus(status_type=UpdateStatusType.FAIL, error_details=str(e))

def print_update_banner(status: RemoteStatus):
    """
    Renders update info.
    Styles: Minimalist, clean, no heavy borders.
    """
    if not status or status.status_type == UpdateStatusType.UP_TO_DATE:
        return

    C_RESET = "\033[0m"
    C_RED = "\033[31m"
    C_GREEN = "\033[32m"
    C_YELLOW = "\033[33m"
    C_BOLD = "\033[1m"
    C_CYAN = "\033[36m"
    C_GREY = "\033[90m"

                                                                     
    
                                                
    if status.status_type == UpdateStatusType.OBSOLETE_SCHEMA:
        print(f"{C_RED}● {t('update-critical-title')}{C_RESET}")
        print(f"  {t('update-critical-desc')}")
        print(f"  {C_CYAN}👉 {status.download_url}{C_RESET}")
        print("")
        return

                                  
    if status.status_type == UpdateStatusType.FAIL:
                                                                            
                                                                    
        print(f"{C_YELLOW}{t('update-error-generic', error=status.error_details)}{C_RESET}")
        
                                                 
        print("")
        print("")
        return

                                
    if status.status_type == UpdateStatusType.ALERT_ONLY and status.alert_message:
        print(f"{C_YELLOW}{C_BOLD}{t('update-alert-prefix')}{C_RESET}")
        _print_wrapped(status.alert_message, indent="  ", color=C_YELLOW)
        print("")
        return

                                             
    if status.status_type == UpdateStatusType.UPDATE_FOUND:
        print(f"{C_GREEN}● {C_BOLD}{t('update-available-title', version=status.latest_version)}{C_RESET}")
        
        if status.alert_message:
            print(f"  {C_YELLOW}{t('update-alert-prefix')} {status.alert_message}{C_RESET}")
            print("")

        shown = status.changelog[:3]
        for entry in shown:
            ver_color = C_RED if entry.importance == 'high' else C_GREEN
            tags = f" {C_GREY}[{', '.join(entry.tags)}]{C_RESET}" if entry.tags else ""
            
            print(f"  {ver_color}v{entry.version}{C_RESET} {tags}")
            _print_wrapped(entry.description, indent="    ")
            
            reqs = []
            if entry.req_pip: reqs.append(t('update-req-pip'))
            if entry.req_config: reqs.append(t('update-req-config'))
            
            if reqs:
                print(f"    {C_YELLOW}⚠ {' + '.join(reqs)}{C_RESET}")
            print("")
            
        if len(status.changelog) > 3:
            rem = len(status.changelog) - 3
            print(f"  {C_GREY}{t('update-more-items', count=rem)}{C_RESET}")
            print("")

        print(f"  {C_CYAN}👉 {t('update-manual-link', url=status.download_url)}{C_RESET}")
        print("")

def _print_wrapped(text: str, indent: str = "", width: int = 70, color: str = ""):
    if not text: return
    words = text.split()
    current_line = []
    current_len = 0
    
    C_RESET = "\033[0m"
    
    for word in words:
        if current_len + len(word) + 1 > width:
            print(f"{indent}{color}{' '.join(current_line)}{C_RESET}")
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + 1
            
    if current_line:
        print(f"{indent}{color}{' '.join(current_line)}{C_RESET}")