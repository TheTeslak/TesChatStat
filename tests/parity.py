import os
import sys
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple

# Path resolution: ascending to project root from /tests
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = PROJECT_ROOT / 'assets' / 'locales'

IGNORE_DIRS = {
    '.git', '.idea', '.vscode', 'venv', '.venv', 'env', 
    '__pycache__', 'dist', 'build', 'tests', 'node_modules',
    '00 REPORTS'
}

# Patterns
RE_PY_STATIC = re.compile(r'(?:\W|^)t\s*\(\s*([\'"])([\w\-\.]+)\1')
RE_PY_DYNAMIC = re.compile(r'(?:\W|^)t\s*\(\s*(f[\'"]|[a-zA-Z_][a-zA-Z0-9_]*)')
RE_FTL_KEY = re.compile(r'^([a-zA-Z][a-zA-Z0-9_\-.]*)\s*=')

class Style:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    GREY = '\033[90m'

def print_section(title: str, icon: str):
    print(f"\n{Style.BOLD}{icon} {title}{Style.RESET}")
    print(f"{Style.GREY}{'-' * 50}{Style.RESET}")

def scan_codebase() -> Tuple[Set[str], List[str]]:
    used_keys = set()
    dynamic_calls = []
    
    for root_dir, dirs, filenames in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in filenames:
            if f.endswith('.py') and f != 'parity.py':
                file_path = Path(root_dir) / f
                try:
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.splitlines()
                    
                    for idx, line in enumerate(lines):
                        # Static matches
                        for _, key in RE_PY_STATIC.findall(line):
                            used_keys.add(key)
                        
                        # Dynamic calls (f-strings or variables)
                        if RE_PY_DYNAMIC.search(line) and 'def t(' not in line:
                            dynamic_calls.append(f"{rel_path}:{idx + 1}  {line.strip()}")
                except Exception as e:
                    print(f"{Style.RED}⚠ Error scanning {f}: {e}{Style.RESET}")
    return used_keys, dynamic_calls

def load_locale_keys(lang: str) -> Set[str]:
    keys = set()
    lang_dir = LOCALES_DIR / lang
    
    # Files to check: specific lang folder + root locales folder (for art.ftl)
    search_paths = []
    if lang_dir.exists():
        search_paths.extend(list(lang_dir.glob('*.ftl')))
    
    # Also check the base locales directory for shared files like art.ftl
    search_paths.extend(list(LOCALES_DIR.glob('*.ftl')))

    for ftl_path in search_paths:
        try:
            content = ftl_path.read_text(encoding='utf-8')
            for line in content.splitlines():
                match = RE_FTL_KEY.match(line)
                if match:
                    keys.add(match.group(1))
        except Exception:
            continue
    return keys

def main():
    print(f"\n{Style.BOLD}{Style.CYAN}🚀 Localization Audit Utility{Style.RESET}")
    print(f"{Style.GREY}Scanning Project Root: {PROJECT_ROOT}{Style.RESET}")

    # 1. Extraction
    used_keys, dynamic_calls = scan_codebase()
    languages = ['en', 'ru']
    locales_data = {lang: load_locale_keys(lang) for lang in languages}
    
    # 2. Dynamic Warnings
    if dynamic_calls:
        print_section(f"Dynamic References ({len(dynamic_calls)})", "⚠️")
        print(f"   {Style.YELLOW}Found calls using variables or f-strings.{Style.RESET}")
        print(f"   {Style.YELLOW}The following keys might be used but cannot be verified:{Style.RESET}\n")
        for call in dynamic_calls[:8]:
            print(f"   {Style.GREY}•{Style.RESET} {call}")
        if len(dynamic_calls) > 8:
            print(f"   {Style.GREY}... and {len(dynamic_calls) - 8} more paths.{Style.RESET}")

    # 3. Individual Language Reports
    has_critical_error = False
    
    for lang, defined_keys in locales_data.items():
        print_section(f"Locale integrity: {lang.upper()}", "🌍")
        
        missing = used_keys - defined_keys
        unused = defined_keys - used_keys
        
        if not defined_keys:
            print(f"   {Style.RED}❌ No definition files found for this language.{Style.RESET}")
            continue

        if missing:
            has_critical_error = True
            print(f"   {Style.RED}❌ Missing Definitions ({len(missing)}){Style.RESET}")
            for k in sorted(missing):
                print(f"     • {k}")
        
        if unused:
            print(f"   {Style.YELLOW}🗑️  Unused Definitions ({len(unused)}){Style.RESET}")
            print(f"     {Style.GREY}(Check dynamic calls before removing){Style.RESET}")
            for k in sorted(unused):
                print(f"     • {k}")

        if not missing and not unused:
            print(f"   {Style.GREEN}✨ Comprehensive coverage. No discrepancies found.{Style.RESET}")

    # 4. Cross-Language Parity Check
    print_section("Cross-Language Synchronization", "⚖️")
    en_keys = locales_data.get('en', set())
    ru_keys = locales_data.get('ru', set())

    only_en = en_keys - ru_keys
    only_ru = ru_keys - en_keys

    if not only_en and not only_ru:
        print(f"   {Style.GREEN}✨ Perfect parity. All languages share the same key set.{Style.RESET}")
    else:
        if only_en:
            print(f"   {Style.YELLOW}⚠️  Present in EN but missing in RU:{Style.RESET}")
            for k in sorted(only_en): print(f"     • {k}")
        if only_ru:
            print(f"   {Style.YELLOW}⚠️  Present in RU but missing in EN:{Style.RESET}")
            for k in sorted(only_ru): print(f"     • {k}")

    # 5. Final Verdict
    print(f"\n{Style.GREY}{'='*50}{Style.RESET}")
    if has_critical_error:
        print(f"   {Style.RED}{Style.BOLD}AUDIT FAILED:{Style.RESET} Missing keys may cause UI placeholders.")
        sys.exit(1)
    else:
        print(f"   {Style.GREEN}{Style.BOLD}AUDIT PASSED:{Style.RESET} Codebase is healthy.")
        print(f"{Style.GREY}{'='*50}{Style.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Style.RED}Audit cancelled by user.{Style.RESET}")