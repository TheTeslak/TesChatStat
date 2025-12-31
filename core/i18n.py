import os
import sys
import config

try:
    from fluent.runtime import FluentLocalization, FluentResourceLoader
except ImportError:
    print("❌ Critical Error: 'fluent.runtime' not found.")
    print("👉 Run: pip install fluent.runtime>=0.4.0")
    sys.exit(1)

def get_loader():
    """
    Configures the loader to search in two locations:
    1. assets/locales/{locale}/ (e.g., ru/main.ftl)
    2. assets/locales/ (e.g., art.ftl)
    """
    locales_dir = os.path.join(config.BASE_DIR, 'assets', 'locales')
    
    roots = [
        os.path.join(locales_dir, "{locale}"),                                       
        locales_dir                                                                          
    ]
    
    return FluentResourceLoader(roots)

class I18n:
    def __init__(self, locale: str):
        self.loader = get_loader()
        self.locale = locale
        
                                                                           
        self.resource_files = [
            'art.ftl',
            'main.ftl',
            'cli.ftl',
            'report.ftl', 
            'charts.ftl',
            'errors.ftl'
        ]
        
        self.l10n = FluentLocalization(
            [locale, 'en'], 
            self.resource_files, 
            self.loader
        )

    def get(self, key: str, **kwargs) -> str:
        try:
            val = self.l10n.format_value(key, kwargs)
                                                                                                                
            return val if val != key else f"[{key}]"
        except Exception:
            return f"[{key}]"

_current_i18n = None

def init_i18n(locale: str = 'ru'):
    global _current_i18n
    _current_i18n = I18n(locale)

def t(key: str, **kwargs) -> str:
    if _current_i18n is None:
        return key
    return _current_i18n.get(key, **kwargs)