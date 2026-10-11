import json, os, sys

_strings = {}
_lang = "de"

LANGUAGES = {
    "de": {"flag": "🇩🇪", "file": "de.json"},
    "en": {"flag": "🇬🇧", "file": "en.json"},
    "es": {"flag": "🇪🇸", "file": "es.json"},
    "fr": {"flag": "🇫🇷", "file": "fr.json"},
}

def _bundle_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def load_language(lang_code):
    global _strings, _lang
    _lang = lang_code
    path = os.path.join(_bundle_dir(), "locales", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _strings = json.load(f)
    except Exception:
        _strings = {}

def t(key):
    return _strings.get(key, key)

def current_lang():
    return _lang
