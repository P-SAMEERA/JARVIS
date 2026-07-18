import re
import subprocess
import sys
import webbrowser
import urllib.parse

from helpers import safe_print

# ============================================================
# Browser / Site Resolution
#
# This replaces the old fixed LOCAL_URL_ACTIONS dict of exact
# phrases ("open youtube", "open google", ...) with a general
# "site name -> URL" map plus a real browser-launch layer, so
# requests like "open youtube in brave" or "launch github using
# chrome" are actually understood as (site, browser) pairs
# instead of being pattern-matched verbatim.
# ============================================================

SITE_SHORTCUTS = {

    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "chat gpt": "https://chatgpt.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "stack overflow": "https://stackoverflow.com",
    "stackoverflow": "https://stackoverflow.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "maps": "https://maps.google.com",
    "netflix": "https://netflix.com",
    "amazon": "https://amazon.com",
    "reddit": "https://reddit.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "linkedin": "https://linkedin.com",
    "spotify": "https://open.spotify.com",
    "whatsapp": "https://web.whatsapp.com",
    "drive": "https://drive.google.com",
    "calendar": "https://calendar.google.com",

}

# Per-OS launch commands for specific browsers. "%s" style args
# aren't needed since we just append the URL as the final arg.
BROWSER_LAUNCHERS = {

    "win32": {
        "chrome": ["chrome.exe"],
        "brave": ["brave.exe"],
        "firefox": ["firefox.exe"],
        "edge": ["msedge.exe"],
    },

    "darwin": {
        "chrome": ["open", "-a", "Google Chrome"],
        "brave": ["open", "-a", "Brave Browser"],
        "firefox": ["open", "-a", "Firefox"],
        "edge": ["open", "-a", "Microsoft Edge"],
    },

    "linux": {
        "chrome": ["google-chrome"],
        "brave": ["brave-browser"],
        "firefox": ["firefox"],
        "edge": ["microsoft-edge"],
    },

}

# Maps loose spoken/typed phrasing to a canonical browser key.
BROWSER_ALIASES = {

    "chrome": "chrome",
    "google chrome": "chrome",
    "brave": "brave",
    "brave browser": "brave",
    "firefox": "firefox",
    "mozilla": "firefox",
    "mozilla firefox": "firefox",
    "edge": "edge",
    "microsoft edge": "edge",

}

# "open X", "launch X", "pull up X" [in|on|using|with <browser>]
OPEN_PATTERN = re.compile(

    r"^(?:open|launch|pull up|start)\s+(.+?)"
    r"(?:\s+(?:in|on|using|with)\s+(.+))?$",

    re.IGNORECASE

)

def get_platform_key() -> str:

    if sys.platform.startswith("win"):
        return "win32"

    if sys.platform == "darwin":
        return "darwin"

    return "linux"


def resolve_browser_alias(text: str):

    text = text.strip().lower()

    if text in BROWSER_ALIASES:
        return BROWSER_ALIASES[text]

    for alias, key in BROWSER_ALIASES.items():

        if alias in text:
            return key

    return None


def resolve_site_url(name: str) -> str:

    name = name.strip().lower().strip(".")

    if name in SITE_SHORTCUTS:
        return SITE_SHORTCUTS[name]

    # loose match: "you tube", "the youtube site", etc.
    for key, url in SITE_SHORTCUTS.items():

        if key in name or name in key:
            return url

    # looks like a bare domain, e.g. "example.com"
    if re.match(r"^[\w.-]+\.[a-z]{2,}(/.*)?$", name):

        if not name.startswith("http"):
            return f"https://{name}"

        return name

    # fall back to a Google search for whatever was asked for
    return f"https://www.google.com/search?q={urllib.parse.quote(name)}"


def parse_open_request(query: str):
    """
    Parses phrases like:
      "open youtube"
      "open youtube in brave"
      "launch github using chrome"
      "pull up netflix on firefox"

    Returns (url, browser_key_or_None, site_label) or None if the
    query doesn't look like an "open something" request at all.
    """

    match = OPEN_PATTERN.match(query.strip())

    if not match:
        return None

    site_part = match.group(1).strip()
    browser_part = match.group(2)

    browser = None

    if browser_part:
        browser = resolve_browser_alias(browser_part)

    url = resolve_site_url(site_part)

    return url, browser, site_part


def open_url_in_browser(url: str, browser: str = None) -> str:
    """
    Launches `url`. If `browser` is a known key, tries to launch
    that specific browser; otherwise (or on failure) falls back
    to the OS default browser via webbrowser.open.

    Returns a short human-readable label of what was actually used,
    so callers can tell the user what happened.
    """

    if not browser:
        webbrowser.open(url)
        return "your default browser"

    platform_key = get_platform_key()
    launcher = BROWSER_LAUNCHERS.get(platform_key, {}).get(browser)

    if not launcher:
        webbrowser.open(url)
        return "your default browser (that browser isn't configured for this OS)"

    try:

        subprocess.Popen(launcher + [url])
        return browser

    except FileNotFoundError:

        webbrowser.open(url)
        return f"your default browser ({browser} wasn't found on this system)"

    except Exception as e:

        safe_print(f"[browser] {e}")
        webbrowser.open(url)
        return "your default browser (launch failed)"

