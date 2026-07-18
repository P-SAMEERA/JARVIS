import sys
import threading
import importlib
import re
# ============================================================
# Console Helpers
# ============================================================

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


UNICODE_REPLACEMENTS = {
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
    "\u00A0": " "
}



def contains_phrase(text: str, phrase: str):
    return re.search(
        r"\b" + re.escape(phrase) + r"\b",
        text
    ) is not None


def sanitize_text(text: str) -> str:
    if not text:
        return text

    for bad, good in UNICODE_REPLACEMENTS.items():
        text = text.replace(bad, good)

    return text


def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        print(sanitize_text(" ".join(str(x) for x in args)), **kwargs)


def safe_write(path: str, content: str, mode="a"):
    with open(path, mode, encoding="utf-8") as f:
        f.write(content)


# ============================================================
# Lazy Imports
# ============================================================

_lazy_modules = {}

_lazy_lock = threading.Lock()


def _lazy_import(module_name: str):
    if module_name not in _lazy_modules:
        with _lazy_lock:
            if module_name not in _lazy_modules:
                _lazy_modules[module_name] = importlib.import_module(module_name)

    return _lazy_modules[module_name]