import os
import re
import sys
import json
import time
import queue
import datetime
import threading
import itertools
import traceback
import webbrowser
import subprocess
import importlib
import urllib.parse
import concurrent.futures

import requests


# ============================================================
# Configuration
# ============================================================

CONFIG = {

    # ---------------- AI ----------------

    "OLLAMA_HOST": "http://localhost:11434",

    "MODEL_GENERAL": "gemma3:4b",

    "MODEL_CODE": "qwen3:8b",

    # ---------------- Memory ----------------

    "MEMORY_FILE": "memory.json",

    "MEMORY_MAX_RAW_TURNS": 20,

    # ---------------- Agent ----------------

    "MAX_AGENT_STEPS": 6,

    "TOOL_TIMEOUT": 20,

    # ---------------- Audio ----------------

    "VOICE_INDEX": 1,

    "SOUNDS": {

        "wake": "assets/wake.mp3",

        "screenshot": "assets/screenshot.mp3",

        "success": "assets/success.mp3",

        "error": "assets/error.mp3",

        "startup": "assets/startup.mp3",

        "shutdown": "assets/shutdown.mp3"

    },

    # ---------------- Files ----------------

    "CODE_OUTPUT": "generated_code.txt",

    "CHAT_OUTPUT": "response.txt",

    "COMMAND_OUTPUT": "commands.txt",

    "AGENT_OUTPUT": "agentic_response.txt",

    "AGENT_LOG": "agent_log.txt",

    "SCREENSHOT_DIR": "screenShots"

}


OLLAMA_HOST = CONFIG["OLLAMA_HOST"]

MODEL_GENERAL = CONFIG["MODEL_GENERAL"]

MODEL_CODE = CONFIG["MODEL_CODE"]

MEMORY_FILE = CONFIG["MEMORY_FILE"]

MEMORY_MAX_RAW_TURNS = CONFIG["MEMORY_MAX_RAW_TURNS"]

AGENT_MAX_STEPS = CONFIG["MAX_AGENT_STEPS"]

TOOL_TIMEOUT_SECONDS = CONFIG["TOOL_TIMEOUT"]


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


# ============================================================
# Sound Manager
# ============================================================

class SoundManager:

    @staticmethod
    def play(sound_name: str):

        try:

            sound_path = CONFIG["SOUNDS"].get(sound_name)

            if not sound_path:
                return

            if not os.path.exists(sound_path):
                return

            pydub = _lazy_import("pydub")
            playback = _lazy_import("pydub.playback")

            sound = pydub.AudioSegment.from_file(sound_path)

            playback.play(sound)

        except Exception as e:

            safe_print(f"[sound] {e}")


# ============================================================
# Startup Banner
# ============================================================

def startup_banner():

    print()

    print("=" * 60)

    print("                 JARVIS v0.3")

    print("=" * 60)

    print(f"General Model : {MODEL_GENERAL}")

    print(f"Code Model    : {MODEL_CODE}")

    print(f"Ollama        : {OLLAMA_HOST}")

    print(f"Memory File   : {MEMORY_FILE}")

    print("=" * 60)

    print()

# ============================================================
# Ollama Client
# ============================================================
def ollama_generate(
    system_prompt: str,
    user_prompt: str,
    model: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:

    payload = {
        "model": model,
        "messages": [
             {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:

        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=180,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            f"Couldn't connect to Ollama at {OLLAMA_HOST}. "
            f"Is 'ollama serve' running?"
        )

    except requests.exceptions.HTTPError as e:

        raise RuntimeError(
            f"Ollama rejected the request ({e}). "
            f"Model '{model}' may not exist."
        )

    data = response.json()

    return (
        data.get("message", {})
            .get("content", "")
            .strip()
    )


# ============================================================
# Persistent Memory
# ============================================================

class Memory:

    def __init__(self):

        self.path = MEMORY_FILE

        self.lock = threading.Lock()

        self.data = self._load()


    # ---------------- Internal ----------------

    def _load(self):

        if os.path.exists(self.path):

            try:

                with open(
                    self.path,
                    "r",
                    encoding="utf-8",
                ) as f:

                    return json.load(f)

            except Exception as e:

                safe_print(f"[memory] {e}")

        return {
            "summary": "",
            "turns": [],
        }


    def _save(self):

        try:

            with open(
                self.path,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    self.data,
                    f,
                    ensure_ascii=False,
                    indent=4,
                )

        except Exception as e:

            safe_print(f"[memory] {e}")


    # ---------------- Public ----------------

    def remember(
        self,
        role: str,
        content: str,
    ):

        with self.lock:

            self.data["turns"].append(
                {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

            if len(self.data["turns"]) > MEMORY_MAX_RAW_TURNS:

                self._compress()

            self._save()


    def get_context(self) -> str:

        with self.lock:

            context = []

            if self.data["summary"]:

                context.append(
                    "Long Term Memory\n"
                    + self.data["summary"]
                )

            if self.data["turns"]:

                recent = "\n".join(

                    f"{item['role']}: {item['content']}"

                    for item in self.data["turns"][-6:]

                )

                context.append(
                    "Recent Conversation\n"
                    + recent
                )

            return "\n\n".join(context)


    # ---------------- Compression ----------------

    def _compress(self):

        keep = MEMORY_MAX_RAW_TURNS // 2

        old_turns = self.data["turns"][:-keep]

        self.data["turns"] = self.data["turns"][-keep:]

        transcript = "\n".join(

            f"{turn['role']}: {turn['content']}"

            for turn in old_turns

        )

        prompt = f"""
Update the running memory.

Current Summary:

{self.data['summary']}

Conversation:

{transcript}

Rules:

- Maximum 150 words.
- Store only facts.
- Store user preferences.
- Store decisions.
- Store ongoing projects.
- Ignore greetings.
- Third-person writing.
"""

        try:

            summary = ollama_generate(

                system_prompt=(
                    "You are the memory engine "
                    "for JARVIS."
                ),

                user_prompt=prompt,

                model=MODEL_GENERAL,

                max_tokens=300,

                temperature=0.2,

            )

            if summary:

                self.data["summary"] = summary.strip()

        except Exception as e:

            safe_print(f"[memory] compression failed : {e}")


MEMORY = Memory()

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


# ============================================================
# Tools
# ============================================================

DANGEROUS_SHELL_PATTERNS = [

    r"rm\s+-rf\s+/",
    r"del\s+/f",
    r"format\s+[a-z]:",
    r"mkfs",
    r"diskpart",
    r"shutdown",
    r"reg\s+delete",
    r"cipher\s+/w",
    r"vssadmin",
    r"dd\s+if=",

]


class ToolManager:

    @staticmethod
    def web_search(query: str) -> str:

        try:

            response = requests.get(

                "https://html.duckduckgo.com/html/",

                params={
                    "q": query
                },

                headers={
                    "User-Agent": "Mozilla/5.0"
                },

                timeout=10

            )

            response.raise_for_status()

        except Exception as e:

            return f"Web search failed : {e}"

        def clean(text):

            return re.sub(
                r"<.*?>",
                "",
                text
            ).strip()

        titles = re.findall(
            r'class="result__a"[^>]*>(.*?)</a>',
            response.text,
            re.DOTALL
        )

        snippets = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</a>',
            response.text,
            re.DOTALL
        )

        results = []

        for title, snippet in zip(titles[:5], snippets[:5]):

            results.append(

                f"- {clean(title)} : {clean(snippet)}"

            )

        if not results:

            return "No results found."

        return "\n".join(results)


    @staticmethod
    def read_file(path: str) -> str:

        try:

            path = path.strip().strip('"')

            with open(

                path,

                "r",

                encoding="utf-8",

                errors="replace"

            ) as file:

                return file.read()[:4000]

        except Exception as e:

            return f"Read failed : {e}"


    @staticmethod
    def write_file(argument: str) -> str:

        try:

            if "::" not in argument:

                return (
                    "Use format : path::content"
                )

            path, content = argument.split(
                "::",
                1
            )

            path = path.strip().strip('"')

            parent = os.path.dirname(path)

            if parent:

                os.makedirs(
                    parent,
                    exist_ok=True
                )

            with open(

                path,

                "w",

                encoding="utf-8"

            ) as file:

                file.write(content)

            return f"Saved to {path}"

        except Exception as e:

            return f"Write failed : {e}"


    @staticmethod
    def run_shell(command: str) -> str:

        command = command.strip()

        for pattern in DANGEROUS_SHELL_PATTERNS:

            if re.search(

                pattern,

                command,

                re.IGNORECASE

            ):

                return (
                    "Command blocked for safety."
                )

        try:

            result = subprocess.run(

                command,

                shell=True,

                capture_output=True,

                text=True,

                timeout=TOOL_TIMEOUT_SECONDS

            )

            output = (

                result.stdout

                +

                result.stderr

            )

            if not output.strip():

                return "Command executed successfully."

            return output[:4000]

        except subprocess.TimeoutExpired:

            return "Command timed out."

        except Exception as e:

            return f"Shell failed : {e}"


    @staticmethod
    def open_browser(argument: str) -> str:
        """
        Agent-facing tool. Argument format: "site::browser"
        (browser half is optional), e.g.:
          "youtube::brave"
          "github.com/anthropics/claude"
          "reddit.com::firefox"
        """

        if "::" in argument:
            site, browser_raw = argument.split("::", 1)
            browser = resolve_browser_alias(browser_raw) if browser_raw.strip() else None
        else:
            site = argument
            browser = None

        site = site.strip()

        if not site:
            return "No site or URL provided."

        url = resolve_site_url(site)
        used = open_url_in_browser(url, browser)

        return f"Opened {site} ({url}) in {used}."


TOOL_REGISTRY = {

    "web_search": ToolManager.web_search,

    "read_file": ToolManager.read_file,

    "write_file": ToolManager.write_file,

    "run_shell": ToolManager.run_shell,

    "open_browser": ToolManager.open_browser,

}


# ============================================================
# Agent Loop
# ============================================================

ACTION_REGEX = re.compile(

    r"Action:\s*(\w+)\[(.*)\]",

    re.DOTALL

)

FINAL_REGEX = re.compile(

    r"Final Answer:\s*(.*)",

    re.DOTALL

)


AGENT_SYSTEM_PROMPT = """
You are JARVIS.

Solve the user's request step-by-step.

Available tools:

- web_search[query]
- read_file[path]
- write_file[path::content]
- run_shell[command]
- open_browser[site::browser]  (browser is optional, e.g. open_browser[youtube::brave] or open_browser[youtube])

Only use one tool at a time.

Reply using ONLY one format.

Thought: ...

Action: tool[input]

OR

Thought: ...

Final Answer: ...
"""


def log_agent_trace(

    goal: str,

    trace: str

):

    safe_write(

        CONFIG["AGENT_LOG"],

        f"""
GOAL

{goal}

TRACE

{trace}

TIME

{datetime.datetime.now()}

{'=' * 80}

"""

    )


def agent_loop(

    goal: str,

    memory_context: str = ""

):

    scratchpad = ""

    for _ in range(AGENT_MAX_STEPS):

        prompt = ""

        if memory_context:

            prompt += (

                memory_context

                +

                "\n\n"

            )

        prompt += f"Goal : {goal}\n\n"

        prompt += scratchpad

        try:

            response = ollama_generate(

                system_prompt=AGENT_SYSTEM_PROMPT,

                user_prompt=prompt,

                model=MODEL_GENERAL,

                max_tokens=400,

                temperature=0.3

            )

        except Exception as e:

            return f"Agent Error : {e}"

        final = FINAL_REGEX.search(response)

        if final:

            scratchpad += "\n" + response

            log_agent_trace(

                goal,

                scratchpad

            )

            return final.group(1).strip()

        action = ACTION_REGEX.search(response)

        if not action:

            log_agent_trace(

                goal,

                scratchpad

                +

                response

            )

            return response.strip()

        tool_name = action.group(1).strip()

        tool_input = action.group(2).strip()

        tool = TOOL_REGISTRY.get(tool_name)

        if tool:

            observation = tool(tool_input)

        else:

            observation = (

                f"Unknown Tool : {tool_name}"

            )

        scratchpad += f"""

{response}

Observation:

{observation}

"""

    log_agent_trace(

        goal,

        scratchpad

    )

    return (
        "Maximum reasoning steps reached.\n\n"

        +

        scratchpad[-1000:]

    )

# ============================================================
# Speech Engine
# ============================================================

class SpeechWorker:

    def __init__(self):

        self.queue = queue.Queue()

        self.thread = threading.Thread(

            target=self._run,

            name="jarvis-tts",

            daemon=True

        )

        self.thread.start()


    def _run(self):

        pyttsx4 = _lazy_import("pyttsx4")

        engine = pyttsx4.init()

        voices = engine.getProperty("voices")

        if voices:

            voice_index = CONFIG["VOICE_INDEX"]

            if voice_index >= len(voices):

                voice_index = 0

            engine.setProperty(

                "voice",

                voices[voice_index].id

            )

        while True:

            text, completed = self.queue.get()

            try:

                engine.say(text)

                engine.runAndWait()

            except Exception as e:

                safe_print(f"[tts] {e}")

            finally:

                completed.set()


    def speak(self, text: str):

        finished = threading.Event()

        self.queue.put(

            (

                sanitize_text(text),

                finished

            )

        )

        finished.wait()


# ============================================================
# Speech Manager
# ============================================================

_speech_worker = None

_speech_lock = threading.Lock()


def get_speech_worker():

    global _speech_worker

    if _speech_worker is None:

        with _speech_lock:

            if _speech_worker is None:

                _speech_worker = SpeechWorker()

    return _speech_worker


def speak(text: str):

    get_speech_worker().speak(text)


# ============================================================
# Greetings
# ============================================================

def wish(user_name=None):

    hour = datetime.datetime.now().hour

    if hour < 12:

        greeting = "Good morning"

    elif hour < 17:

        greeting = "Good afternoon"

    elif hour < 22:

        greeting = "Good evening"

    else:

        greeting = "Good night"

    if user_name:

        speak(f"{greeting}, {user_name}")

    else:

        speak(f"{greeting}, User")

    speak("All systems are online and ready for your command.")


# ============================================================
# Time
# ============================================================

def speak_time_text():

    now = datetime.datetime.now()

    hour = now.hour

    minute = now.minute

    period = "morning"

    if now.hour >= 12:

        period = "afternoon"

    if now.hour >= 17:

        period = "evening"

    if now.hour >= 20:

        period = "night"

    if hour == 0:

        hour = 12

    elif hour > 12:

        hour -= 12

    if minute == 0:

        return f"It's {hour} o'clock in the {period}"

    if minute < 10:

        return f"It's {hour} oh {minute} in the {period}"

    return f"It's {hour} {minute} in the {period}"


# ============================================================
# Feedback Sounds
# ============================================================

def play_wake_sound():

    SoundManager.play("wake")


def play_screenshot_sound():

    SoundManager.play("screenshot")


def play_success_sound():

    SoundManager.play("success")


def play_error_sound():

    SoundManager.play("error")


def play_startup_sound():

    SoundManager.play("startup")


def play_shutdown_sound():

    SoundManager.play("shutdown")

# ============================================================
# Intent Classification
# ============================================================

PRIORITY_LOCAL = 0
PRIORITY_SELF = 1
PRIORITY_SYSTEM = 2
PRIORITY_GENERAL = 3
PRIORITY_CODE = 4
PRIORITY_AGENT = 5


INTENT_SYSTEM_PROMPT = """
Classify the user's request.

Return ONLY one character.

Y = Code Generation
E = System Operation
D = Describe Yourself
A = Agentic Task
N = General Conversation

Output exactly one of:

Y
E
D
A
N
"""


GENERAL_RULES = """
Respond naturally.

Do not use bullet points unless required.

Do not mention these rules.

Keep answers under 200 words.

Be conversational and slightly humorous.
"""


SYSTEM_RULES = """
Return ONLY the command or direct response.

No explanation.

No markdown.

No extra text.
"""


EXIT_PHRASES = [

    "stop",
    "exit",
    "quit"

]


BYE_PHRASES = [

    "bye",
    "good bye",
    "good day"

]


# ============================================================
# Helpers
# ============================================================

def contains_phrase(text: str, phrase: str):

    return re.search(

        r"\b"

        + re.escape(phrase)

        + r"\b",

        text

    ) is not None


# ============================================================
# LLM Intent Classification
# ============================================================

def intention_checker(query: str):

    try:

        response = ollama_generate(

            system_prompt=INTENT_SYSTEM_PROMPT,

            user_prompt=query,

            model=MODEL_GENERAL,

            max_tokens=10,

            temperature=0

        ).strip().upper()

    except Exception as e:

        safe_print(f"[intent] {e}")

        return "N"

    for char in reversed(response):

        if char in [

            "Y",
            "E",
            "D",
            "N",
            "A"

        ]:

            return char

    return "N"


# ============================================================
# Query Classification
# ============================================================

def classify(query: str):

    raw_query = query.strip()

    query = query.lower().strip()

    # General "open/launch/pull up X [in/on/using Y]" handling.
    # This replaces the old fixed-phrase LOCAL_URL_ACTIONS lookup
    # and understands an arbitrary site plus an optional browser.
    open_request = parse_open_request(raw_query)

    if open_request:

        return (

            PRIORITY_LOCAL,

            "open",

            open_request

        )

    if contains_phrase(

        query,

        "screenshot"

    ):

        return (

            PRIORITY_LOCAL,

            "screenshot",

            None

        )

    if contains_phrase(

        query,

        "time"

    ):

        return (

            PRIORITY_LOCAL,

            "time",

            None

        )

    if any(

        contains_phrase(query, phrase)

        for phrase in EXIT_PHRASES

    ):

        return (

            PRIORITY_LOCAL,

            "exit",

            None

        )

    if any(

        contains_phrase(query, phrase)

        for phrase in BYE_PHRASES

    ):

        return (

            PRIORITY_LOCAL,

            "bye",

            None

        )

    if len(query) < 2:

        return (

            PRIORITY_LOCAL,

            "noop",

            None

        )

    tag = intention_checker(query)

    priorities = {

        "D": PRIORITY_SELF,

        "E": PRIORITY_SYSTEM,

        "N": PRIORITY_GENERAL,

        "Y": PRIORITY_CODE,

        "A": PRIORITY_AGENT

    }

    return (

        priorities.get(

            tag,

            PRIORITY_GENERAL

        ),

        tag,

        query

    )
# ============================================================
# Thread Priority
# ============================================================

IS_WINDOWS = sys.platform.startswith("win")

THREAD_PRIORITY_BELOW_NORMAL = -1
THREAD_PRIORITY_ABOVE_NORMAL = 1


def set_current_thread_priority(level: int):

    if not IS_WINDOWS:
        return

    try:

        import ctypes

        handle = ctypes.windll.kernel32.GetCurrentThread()

        ctypes.windll.kernel32.SetThreadPriority(
            handle,
            level
        )

    except Exception as e:

        safe_print(f"[priority] {e}")


# ============================================================
# Priority Scheduler
# ============================================================

class PriorityScheduler:

    def __init__(self, max_workers=3):

        self.queue = queue.PriorityQueue()

        self.counter = itertools.count()

        self.pending = 0

        self.pending_lock = threading.Lock()

        self.speak_lock = threading.Lock()

        self.running = True

        self.mic_listener = None

        self.state_changed = threading.Event()

        self.executor = concurrent.futures.ThreadPoolExecutor(

            max_workers=max_workers,

            thread_name_prefix="jarvis-worker"

        )

        self.dispatcher = threading.Thread(

            target=self._dispatch_loop,

            daemon=True,

            name="jarvis-dispatcher"

        )

        self.dispatcher.start()


    # ========================================================
    # Queue State
    # ========================================================

    def register_pending(self):

        with self.pending_lock:

            self.pending += 1

            became_busy = self.pending == 1

        if became_busy:

            self.state_changed.set()

        return self.pending


    def task_completed(self):

        with self.pending_lock:

            self.pending -= 1

            became_idle = self.pending == 0

        if became_idle:

            self.state_changed.set()


    def is_busy(self):

        with self.pending_lock:

            return self.pending > 0


    def wait_for_state_change(self, timeout=None):

        fired = self.state_changed.wait(timeout)

        if fired:

            self.state_changed.clear()

        return fired


    # ========================================================
    # Submit Tasks
    # ========================================================

    def submit(

        self,

        priority,

        function,

        *args,

        **kwargs

    ):

        pending = self.register_pending()

        safe_print(

            f"[scheduler] queued "

            f"(priority={priority}, pending={pending})"

        )

        self.queue.put(

            (

                priority,

                next(self.counter),

                function,

                args,

                kwargs

            )

        )


    def run_now(

        self,

        function,

        *args,

        **kwargs

    ):

        pending = self.register_pending()

        safe_print(

            f"[scheduler] "

            f"executing immediately "

            f"(pending={pending})"

        )

        self.executor.submit(

            self._execute,

            function,

            args,

            kwargs

        )


    # ========================================================
    # Dispatcher
    # ========================================================

    def _dispatch_loop(self):

        set_current_thread_priority(

            THREAD_PRIORITY_BELOW_NORMAL

        )

        while self.running:

            try:

                priority, _, function, args, kwargs = self.queue.get(

                    timeout=0.5

                )

            except queue.Empty:

                continue

            self.executor.submit(

                self._execute,

                function,

                args,

                kwargs

            )


    def _execute(

        self,

        function,

        args,

        kwargs

    ):

        set_current_thread_priority(

            THREAD_PRIORITY_BELOW_NORMAL

        )

        try:

            function(

                *args,

                **kwargs

            )

        except Exception as e:

            safe_print(

                f"[scheduler] {e}"

            )

            traceback.print_exc()

        finally:

            self.task_completed()


    # ========================================================
    # Speech
    # ========================================================

    def speak_safe(self, text: str):

        text = sanitize_text(text)

        with self.speak_lock:

            if self.mic_listener:

                self.mic_listener.pause()

            try:

                speak(text)

            finally:

                if self.mic_listener:

                    self.mic_listener.resume()


    # ========================================================
    # Shutdown
    # ========================================================

    def shutdown(self, wait=True):

        self.running = False

        self.executor.shutdown(

            wait=wait,

            cancel_futures=True

        )


# ============================================================
# Global Shutdown Event
# ============================================================

shutdown_event = threading.Event()

# ============================================================
# Task Handlers
# ============================================================

def task_open_url(scheduler, action):

    url, browser, label = action

    used = open_url_in_browser(url, browser)

    scheduler.speak_safe(f"Opening {label} in {used}.")


def task_screenshot(scheduler):

    pyautogui = _lazy_import("pyautogui")

    os.makedirs(

        CONFIG["SCREENSHOT_DIR"],

        exist_ok=True

    )

    filename = datetime.datetime.now().strftime(

        "screenshot_%Y-%m-%d_%H-%M-%S.png"

    )

    path = os.path.join(

        CONFIG["SCREENSHOT_DIR"],

        filename

    )

    # Camera shutter first
    play_screenshot_sound()

    screenshot = pyautogui.screenshot()

    screenshot.save(path)

    scheduler.speak_safe(

        "Screenshot captured successfully."

    )


def task_time(scheduler):

    scheduler.speak_safe(

        speak_time_text()

    )


def task_exit(scheduler):

    play_shutdown_sound()

    scheduler.speak_safe(

        "Have a great day."

    )

    shutdown_event.set()


def task_bye(scheduler):

    scheduler.speak_safe(

        "Have a great day."

    )


def task_system_operation(

    scheduler,

    query

):

    response = ollama_generate(

        system_prompt=SYSTEM_RULES,

        user_prompt=query,

        model=MODEL_GENERAL,

        max_tokens=256

    )

    response = sanitize_text(response)

    safe_write(

        CONFIG["COMMAND_OUTPUT"],

        response

        +

        f"\n\n{datetime.datetime.now()}\n\n"

    )

    scheduler.speak_safe(response)


def task_self_description(

    scheduler

):

    scheduler.speak_safe(

        "Greetings. I am Jarvis, your personal local AI assistant."

    )


def task_code(

    scheduler,

    query

):

    response = ollama_generate(

        system_prompt="You are an expert software engineer.",

        user_prompt=query,

        model=MODEL_CODE,

        max_tokens=2048

    )

    response = sanitize_text(response)

    safe_write(

        CONFIG["CODE_OUTPUT"],

        response

        +

        f"\n\n{datetime.datetime.now()}\n\n"

    )

    MEMORY.remember(

        "user",

        query

    )

    MEMORY.remember(

        "assistant",

        "[Generated Code]"

    )

    play_success_sound()

    scheduler.speak_safe(

        "Code generation completed. Please check generated_code.txt."

    )


def task_general(

    scheduler,

    query

):

    context = MEMORY.get_context()

    prompt = GENERAL_RULES

    if context:

        prompt += "\n\n" + context

    response = ollama_generate(

        system_prompt=prompt,

        user_prompt=query,

        model=MODEL_GENERAL,

        max_tokens=400

    )

    response = sanitize_text(response)

    safe_write(

        CONFIG["CHAT_OUTPUT"],

        response

        +

        f"\n\n{datetime.datetime.now()}\n\n"

    )

    MEMORY.remember(

        "user",

        query

    )

    MEMORY.remember(

        "assistant",

        response

    )

    scheduler.speak_safe(

        response.split("!!")[0]

    )


def task_agent(

    scheduler,

    query

):

    context = MEMORY.get_context()

    answer = agent_loop(

        goal=query,

        memory_context=context

    )

    answer = sanitize_text(answer)

    safe_write(

        CONFIG["AGENT_OUTPUT"],

        answer

        +

        f"\n\n{datetime.datetime.now()}\n\n"

    )

    MEMORY.remember(

        "user",

        query

    )

    MEMORY.remember(

        "assistant",

        answer

    )

    play_success_sound()

    if len(answer) > 400:

        spoken = (

            answer[:400]

            +

            "... Please read the complete response from the file."

        )

    else:

        spoken = answer

    scheduler.speak_safe(

        spoken

    )


# ============================================================
# Dispatcher
# ============================================================

def get_task(

    scheduler,

    kind,

    payload,

    query

):

    mapping = {

        "open": (

            task_open_url,

            (scheduler, payload)

        ),

        "screenshot": (

            task_screenshot,

            (scheduler,)

        ),

        "time": (

            task_time,

            (scheduler,)

        ),

        "exit": (

            task_exit,

            (scheduler,)

        ),

        "bye": (

            task_bye,

            (scheduler,)

        ),

        "E": (

            task_system_operation,

            (scheduler, query)

        ),

        "D": (

            task_self_description,

            (scheduler,)

        ),

        "Y": (

            task_code,

            (scheduler, query)

        ),

        "N": (

            task_general,

            (scheduler, query)

        ),

        "A": (

            task_agent,

            (scheduler, query)

        )

    }

    return mapping.get(kind)


def dispatch(

    scheduler,

    priority,

    kind,

    payload,

    query

):

    task = get_task(

        scheduler,

        kind,

        payload,

        query

    )

    if task is None:

        return

    function, args = task

    scheduler.submit(

        priority,

        function,

        *args

    )


def execute_direct(

    scheduler,

    kind,

    payload,

    query

):

    task = get_task(

        scheduler,

        kind,

        payload,

        query

    )

    if task is None:

        return

    function, args = task

    scheduler.run_now(

        function,

        *args

    )


# ============================================================
# Command Processing
# ============================================================

def split_commands(query: str):

    if " and " in query:

        return [

            item.strip()

            for item in query.split(" and ")

            if item.strip()

        ]

    if "." in query:

        return [

            item.strip()

            for item in query.split(".")

            if item.strip()

        ]

    return [

        query.strip()

    ]


def handle_command(

    scheduler,

    query

):

    query = query.strip()

    if not query:

        return

    safe_print(

        f"[dispatch] {query}"

    )

    commands = split_commands(query)

    classified = []

    for command in commands:

        priority, kind, payload = classify(command)

        classified.append(

            (

                priority,

                kind,

                payload,

                command

            )

        )

    tasks = [

        task

        for task in classified

        if task[1] != "noop"

    ]

    if not tasks:

        return

    if len(tasks) == 1:

        priority, kind, payload, command = tasks[0]

        execute_direct(

            scheduler,

            kind,

            payload,

            command

        )

        return

    simple = [

        task

        for task in tasks

        if task[0] == PRIORITY_LOCAL

    ]

    complex_tasks = sorted(

        [

            task

            for task in tasks

            if task[0] != PRIORITY_LOCAL

        ],

        key=lambda x: x[0]

    )

    for priority, kind, payload, command in simple + complex_tasks:

        dispatch(

            scheduler,

            priority,

            kind,

            payload,

            command

        )
# ============================================================
# Microphone Listener
# ============================================================

MIC_DEVICE_INDEX = None

MIN_ENERGY_THRESHOLD = 300

WAKE_WORDS = [

    "jarvis",

    "alex",

    "alexa",

    "alec",

    "elix",

    "sonu"

]


class MicListener:

    def __init__(self, scheduler):

        sr = _lazy_import("speech_recognition")

        self.sr = sr

        self.scheduler = scheduler

        self.recognizer = sr.Recognizer()

        self.recognizer.pause_threshold = 0.8

        self.microphone = sr.Microphone(

            device_index=MIC_DEVICE_INDEX

        )

        self.active = threading.Event()

        self.active.set()

        self._calibrate()


    # ========================================================
    # Calibration
    # ========================================================

    def _calibrate(self):

        safe_print(

            "[mic] Calibrating..."

        )

        with self.microphone as source:

            self.recognizer.adjust_for_ambient_noise(

                source,

                duration=1

            )

        if self.recognizer.energy_threshold < MIN_ENERGY_THRESHOLD:

            self.recognizer.energy_threshold = MIN_ENERGY_THRESHOLD

        safe_print(

            f"[mic] Ready "

            f"(threshold={self.recognizer.energy_threshold:.0f})"

        )


    # ========================================================
    # Listening
    # ========================================================

    def _listen(self):

        with self.microphone as source:

            try:

                return self.recognizer.listen(

                    source,

                    phrase_time_limit=10

                )

            except Exception as e:

                safe_print(f"[mic] {e}")

                return None


    def _recognize(self, audio):

        try:

            text = self.recognizer.recognize_google(

                audio,

                language="en-in"

            )

            safe_print(

                f"Heard : {text}"

            )

            return text

        except self.sr.UnknownValueError:

            return None

        except self.sr.RequestError as e:

            safe_print(

                f"[speech] {e}"

            )

            return None


    # ========================================================
    # Wake Word
    # ========================================================

    def find_wake_word(self, text):

        text = text.lower()

        for wake in WAKE_WORDS:

            if contains_phrase(

                text,

                wake

            ):

                return wake

        return None


    def resolve_command(self, text):

        wake = self.find_wake_word(text)

        if wake is None:

            return None

        play_wake_sound()

        remaining = (

            text.lower()

            .split(

                wake,

                1

            )[1]

            .strip(" ,.")

        )

        if remaining:

            return remaining

        safe_print(

            "[mic] Listening..."

        )

        audio = self._listen()

        if audio is None:

            return None

        command = self._recognize(audio)

        if command:

            return command.strip()

        return None


    # ========================================================
    # Public
    # ========================================================

    def listen_once(self):

        audio = self._listen()

        if audio is None:

            return None

        text = self._recognize(audio)

        if text is None:

            return None

        if self.find_wake_word(text) is None:

            return None

        return self.resolve_command(text)


    # ========================================================
    # TTS Hooks
    # ========================================================

    def pause(self):

        self.active.clear()


    def resume(self):

        self.active.set()
# ============================================================
# JARVIS Bootstrap
# ============================================================

def initialize():

    startup_banner()

    play_startup_sound()

    safe_print("[init] Starting Speech Engine...")
    get_speech_worker()

    safe_print("[init] Connecting to Ollama...")

    try:

        response = requests.get(

            f"{OLLAMA_HOST}/api/tags",

            timeout=5

        )

        response.raise_for_status()

        models = response.json().get("models", [])

        model_names = {

            model["name"]

            for model in models

        }

        if MODEL_GENERAL not in model_names:

            raise RuntimeError(

                f"{MODEL_GENERAL} not found."

            )

        if MODEL_CODE not in model_names:

            raise RuntimeError(

                f"{MODEL_CODE} not found."

            )

        safe_print("[init] Ollama Connected")

    except Exception as e:

        safe_print(f"[init] {e}")

        speak(

            "Unable to connect to Ollama."

        )

        sys.exit(1)

    safe_print("[init] Memory Loaded")

    scheduler = PriorityScheduler(

        max_workers=3

    )

    safe_print("[init] Scheduler Ready")

    microphone = MicListener(

        scheduler

    )

    scheduler.mic_listener = microphone

    safe_print("[init] Microphone Ready")

    wish(None)

    safe_print()

    safe_print("=" * 60)

    safe_print("JARVIS ONLINE")

    safe_print("=" * 60)

    return scheduler, microphone


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    set_current_thread_priority(

        THREAD_PRIORITY_ABOVE_NORMAL

    )

    scheduler = None

    try:

        scheduler, microphone = initialize()

        while not shutdown_event.is_set():

            try:

                command = microphone.listen_once()

                if command:

                    handle_command(

                        scheduler,

                        command

                    )

                while (

                    scheduler.is_busy()

                    and

                    not shutdown_event.is_set()

                ):

                    scheduler.wait_for_state_change(

                        timeout=1

                    )

            except KeyboardInterrupt:

                raise

            except Exception:

                safe_print(

                    "[main] Unexpected Error"

                )

                traceback.print_exc()

    except KeyboardInterrupt:

        safe_print(

            "\n[main] Shutdown Requested"

        )

    finally:

        try:

            play_shutdown_sound()

        except Exception:

            pass

        if scheduler:

            try:

                scheduler.shutdown(

                    wait=False

                )

            except Exception as e:

                safe_print(

                    f"[shutdown] {e}"

                )

        safe_print()

        safe_print("=" * 60)

        safe_print("JARVIS OFFLINE")

        safe_print("=" * 60)

        os._exit(0)