# JARVIS

### A local, voice-driven, tool-using AI agent that runs entirely on your machine.

> "Wake up. Daddy's home."

No cloud API keys. No per-token billing. No data leaving your machine. Just you, a microphone, and two Ollama models doing the thinking while a priority-based Python scheduler does the doing.

This document exists because a codebase this deliberate deserves to be understood, not just run. Every subsystem here was built to answer a specific failure observed in an earlier version — a silent wake word, a crashing Unicode character, a `LOCAL_URL_ACTIONS` dictionary that couldn't tell "brave" from "chrome." What follows is the full anatomy of what replaced those failures.

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Architecture at a Glance](#architecture-at-a-glance)
3. [Installation](#installation)
4. [Configuration Reference](#configuration-reference)
5. [Subsystem Deep Dive](#subsystem-deep-dive)
   - [Console & Encoding Safety](#1-console--encoding-safety)
   - [Lazy Import System](#2-lazy-import-system)
   - [Sound Manager](#3-sound-manager)
   - [The Ollama Client](#4-the-ollama-client)
   - [Persistent Memory](#5-persistent-memory)
   - [Browser & Site Resolution](#6-browser--site-resolution-the-real-intelligence-layer)
   - [Tools & the Tool Registry](#7-tools--the-tool-registry)
   - [The Agent Loop (ReAct)](#8-the-agent-loop-react)
   - [Speech Engine](#9-speech-engine)
   - [Intent Classification](#10-intent-classification)
   - [Priority Scheduler](#11-priority-scheduler)
   - [Task Handlers & Dispatch](#12-task-handlers--dispatch)
   - [Command Splitting](#13-command-splitting)
   - [Microphone Listener](#14-microphone-listener)
   - [Bootstrap & Main Loop](#15-bootstrap--main-loop)
6. [Full Trace: "Jarvis, open YouTube in Brave"](#full-trace-jarvis-open-youtube-in-brave)
7. [Output Files](#output-files)
8. [Known Limitations & Security Notes](#known-limitations--security-notes)
9. [Troubleshooting](#troubleshooting)
10. [Roadmap](#roadmap)

---

## Philosophy

Most "voice assistant" tutorials wire a wake-word library to a single LLM call and stop there. That gets you something that talks. It doesn't get you something that *acts* — and it definitely doesn't get you something that understands the difference between "open youtube" and "open youtube in brave," because a plain string-match dictionary has no concept of "browser" at all. It only knows the exact phrases you hardcoded.

JARVIS is built around a different premise: **intelligence is the ability to decompose a request into structured intent, and reliability is the discipline to execute that intent through deterministic code, not through free-text improvisation.** Concretely, that means:

- The LLM's job is to *understand* — classify intent, extract parameters, decide which tool applies.
- Python's job is to *act* — deterministically, with guardrails, with logging, with a fallback path when something's ambiguous.

Everything below is that principle, implemented function by function.

---

## Architecture at a Glance

```
                         ┌─────────────────────┐
                         │   Microphone Input   │
                         │  (MicListener)       │
                         └──────────┬───────────┘
                                    │  wake word detected
                                    ▼
                         ┌─────────────────────┐
                         │   handle_command()   │
                         │  split_commands()    │
                         └──────────┬───────────┘
                                    │  per sub-command
                                    ▼
                         ┌─────────────────────┐
                         │     classify()       │  ← local pattern match first,
                         │  (Intent Router)      │    LLM fallback (Ollama) second
                         └──────────┬───────────┘
                                    │  (priority, kind, payload)
                                    ▼
                    ┌───────────────────────────────┐
                    │      PriorityScheduler         │
                    │  PriorityQueue + ThreadPoolExec │
                    └───────────────┬────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                      ▼
     task_open_url()        task_code() / task_general()   task_agent()
     task_screenshot()      (ollama_generate → Ollama)     (agent_loop → ReAct
     task_time()                                            → TOOL_REGISTRY)
     task_exit() / bye()
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   scheduler.speak_safe()  │
                         │   → SpeechWorker queue     │
                         └─────────────────────┘
```

Two models, two jobs:

| Model | Config Key | Role |
|---|---|---|
| `gemma3:4b` | `MODEL_GENERAL` | Intent classification, general conversation, memory summarization, ReAct agent reasoning |
| `qwen3:8b` | `MODEL_CODE` | Code generation only |

Everything runs against a local Ollama server at `http://localhost:11434`. There is no external network dependency for inference — `web_search` is the one tool that reaches outside the machine, and only when explicitly invoked by the agent loop.

---

## Installation

### 1. Ollama

```bash
# Install Ollama, then pull the two models this build depends on:
ollama pull gemma3:4b
ollama pull qwen3:8b

# Confirm the server is reachable:
ollama serve
```

`initialize()` will refuse to start if either model is missing from `ollama list` — it checks `/api/tags` at boot and exits with a spoken error rather than failing silently mid-conversation.

### 2. Python dependencies

```bash
pip install requests pyttsx4 pyaudio pyautogui pydub SpeechRecognition
```

`pydub` additionally needs `ffmpeg` on your `PATH` if you want the notification sounds (`wake`, `screenshot`, `success`, `error`, `startup`, `shutdown`) to actually play — silently no-ops otherwise via the `SoundManager.play()` try/except.

### 3. Assets

Populate `assets/` with the six sound files referenced in `CONFIG["SOUNDS"]`, or leave them absent — `SoundManager.play()` checks `os.path.exists()` before attempting playback and returns quietly if a file isn't there.

### 4. Run

```bash
python AI.py
```

---

## Configuration Reference

Every tunable lives in the single `CONFIG` dict at the top of the file — nothing is scattered as a magic number elsewhere.

```python
CONFIG = {
    "OLLAMA_HOST": "http://localhost:11434",   # Ollama server base URL
    "MODEL_GENERAL": "gemma3:4b",               # intent / chat / agent reasoning
    "MODEL_CODE": "qwen3:8b",                   # code generation

    "MEMORY_FILE": "memory.json",               # persistent conversation memory
    "MEMORY_MAX_RAW_TURNS": 20,                 # turns kept verbatim before compression

    "MAX_AGENT_STEPS": 6,                       # ReAct loop ceiling
    "TOOL_TIMEOUT": 20,                         # seconds, applies to run_shell

    "VOICE_INDEX": 1,                           # which SAPI5/TTS voice to use

    "SOUNDS": { ... },                          # six named .mp3 paths

    "CODE_OUTPUT": "generated_code.txt",
    "CHAT_OUTPUT": "response.txt",
    "COMMAND_OUTPUT": "commands.txt",
    "AGENT_OUTPUT": "agentic_response.txt",
    "AGENT_LOG": "agent_log.txt",
    "SCREENSHOT_DIR": "screenShots",
}
```

Nothing else in the file reads a hardcoded path or model string — they all flow through this dict via the module-level constants (`OLLAMA_HOST`, `MODEL_GENERAL`, etc.) unpacked immediately below it. Change a model, change a timeout, change a file path — one place, one edit.

---

## Subsystem Deep Dive

### 1. Console & Encoding Safety

```python
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UNICODE_REPLACEMENTS = { "\u2011": "-", "\u2013": "-", "\u201c": '"', ... }
sanitize_text(text)
safe_print(*args, **kwargs)
safe_write(path, content, mode="a")
```

This exists because of a very specific, very real bug: Windows defaults `stdout` and `open()` to the system codepage (commonly `cp1252`), and LLMs love to output "smart punctuation" — en-dashes, em-dashes, non-breaking hyphens, curly quotes — that `cp1252` cannot encode. The failure mode without this layer is a hard crash mid-response, after the tokens have already been generated and money/compute already spent.

The fix operates at two layers, deliberately redundant:
- `sys.stdout.reconfigure(...)` forces the console itself to UTF-8, with `errors="replace"` as a last-resort net for anything still missed.
- `sanitize_text()` proactively swaps the known troublemakers for ASCII equivalents *before* the text ever reaches TTS, console, or disk — because SAPI5 voices can behave unpredictably on some of these glyphs even when encoding itself isn't the problem.

Every write in the entire codebase goes through `safe_write()`, and every print goes through `safe_print()` (which itself falls back to `sanitize_text()` if a raw `print()` still throws `UnicodeEncodeError`). There is no code path in this file that writes text to disk or terminal without passing through this net.

### 2. Lazy Import System

```python
_lazy_modules = {}
_lazy_lock = threading.Lock()

def _lazy_import(module_name: str):
    if module_name not in _lazy_modules:
        with _lazy_lock:
            if module_name not in _lazy_modules:
                _lazy_modules[module_name] = importlib.import_module(module_name)
    return _lazy_modules[module_name]
```

This is a thread-safe, double-checked-locking singleton cache for heavyweight or optional imports — `pydub`, `pyttsx4`, `pyautogui`, `speech_recognition`. Two things this buys you:

1. **Startup speed.** `pyttsx4.init()` and audio library imports are not free. Deferring them until the moment they're actually needed (first sound played, first TTS utterance, first screenshot) means the script's time-to-first-response is faster.
2. **Graceful degradation.** If `pydub` isn't installed and the user never triggers a sound effect, the program never even tries to import it. A missing optional dependency doesn't crash the whole assistant — it just silently disables the one feature that needed it, caught by the `try/except` in `SoundManager.play()`.

The double-checked lock pattern (`if not in dict` → acquire lock → `if not in dict` again → import) is the standard defense against a race where two threads both see the module missing and both attempt the import simultaneously — relevant here because `PriorityScheduler` runs tasks concurrently across a thread pool, and two tasks could plausibly hit `_lazy_import("pyttsx4")` in the same instant.

### 3. Sound Manager

```python
class SoundManager:
    @staticmethod
    def play(sound_name: str): ...
```

A single static method, six named cues (`wake`, `screenshot`, `success`, `error`, `startup`, `shutdown`), each optional. The lookup is `CONFIG["SOUNDS"].get(sound_name)` — an unrecognized name or a missing file both resolve to a silent no-op rather than an exception, because a notification sound failing should never be the reason a voice command fails.

### 4. The Ollama Client

```python
def ollama_generate(system_prompt, user_prompt, model, max_tokens=1024, temperature=0.7) -> str:
```

The single funnel through which every LLM call in the entire system passes — intent classification, general chat, code generation, memory compression, and every step of the agent's ReAct loop all call this one function with a different `system_prompt`/`model`/`temperature` combination. That centralization matters: there is exactly one place that knows how to talk to Ollama, exactly one place that handles its failure modes, and exactly one payload shape (`/api/chat`, `stream: False`) to reason about.

Two specific failure modes are caught and re-raised as human-readable `RuntimeError`s rather than leaking a raw `requests` traceback:

- `ConnectionError` → *"Couldn't connect to Ollama at `{OLLAMA_HOST}`. Is `ollama serve` running?"* — the single most common failure a fresh setup hits, now diagnosed in the error message itself instead of a stack trace pointing into `urllib3`.
- `HTTPError` → *"Ollama rejected the request. Model `{model}` may not exist."* — catches the case where a model referenced in `CONFIG` was never `ollama pull`ed.

### 5. Persistent Memory

```python
class Memory:
    def remember(role, content): ...
    def get_context() -> str: ...
    def _compress(): ...
```

Memory persists to `memory.json` and survives restarts — unlike the conversation-turn context every earlier version of this assistant lost the moment the process exited. Structurally it's two parts:

- **`summary`** — a running, LLM-generated distillation of everything older than the recent window. Third-person, fact-only, capped at 150 words by prompt instruction.
- **`turns`** — the most recent raw exchanges, kept verbatim.

The compression trigger is simple and bounded: every `remember()` call checks `len(turns) > MEMORY_MAX_RAW_TURNS` (default 20). When it trips, `_compress()` peels off the older half, feeds it to `MODEL_GENERAL` alongside the *existing* summary with an explicit instruction set —

```
- Maximum 150 words.
- Store only facts.
- Store user preferences.
- Store decisions.
- Store ongoing projects.
- Ignore greetings.
- Third-person writing.
```

— and replaces `summary` with the model's output. This means memory doesn't grow unboundedly and doesn't need a vector database or embedding pipeline to stay useful across a long-running session: it's a self-summarizing ring buffer with an LLM as the compression function. `get_context()` is what `task_general()` and `task_agent()` prepend to their prompts — long-term summary first, then the last six raw turns, joined with clear section headers so the model can tell "what I was told once, long ago" apart from "what was just said."

All memory access is `threading.Lock()`-guarded (`self.lock`), because multiple scheduler workers can call `remember()` concurrently.

### 6. Browser & Site Resolution — the Real Intelligence Layer

This is the subsystem that exists specifically to answer *"open youtube in brave"* — the exact request a fixed-phrase dictionary (`LOCAL_URL_ACTIONS`, in the previous version) structurally could not handle, because it had no concept of "browser" as a parameter. Here's how it's decomposed.

**`SITE_SHORTCUTS`** — a name → URL map (`youtube`, `github`, `gmail`, `netflix`, twenty-odd common destinations). Not exhaustive by design; it's a fast path for the common case, not the whole capability.

**`resolve_site_url(name)`** — three-tier resolution, in order:
1. Exact match against `SITE_SHORTCUTS`.
2. Loose substring match (`"the youtube site"` still resolves, because `"youtube" in name` catches it even with surrounding words).
3. If it looks like a bare domain (`re.match(r"^[\w.-]+\.[a-z]{2,}(/.*)?$", name)`), treat it as one and prepend `https://`.
4. Otherwise — and this is the important fallback — **it doesn't fail.** It builds a Google search URL for whatever was asked (`https://www.google.com/search?q=...`). Asking to open something not in the shortcut list still produces a sensible, working action instead of an error.

**`BROWSER_ALIASES`** — normalizes loose spoken/typed phrasing (`"google chrome"`, `"mozilla"`, `"brave browser"`) down to a canonical key (`chrome`, `firefox`, `brave`). `resolve_browser_alias()` tries an exact dict hit first, then falls back to substring containment for anything phrased slightly differently than expected.

**`BROWSER_LAUNCHERS`** — a per-OS (`win32`/`darwin`/`linux`) map from canonical browser key to the actual subprocess launch command, because "launch Chrome" is a completely different `subprocess.Popen` invocation on Windows versus macOS versus Linux. `get_platform_key()` reads `sys.platform` once and every downstream lookup uses that key.

**`OPEN_PATTERN`** — the regex doing the actual sentence parsing:

```python
r"^(?:open|launch|pull up|start)\s+(.+?)(?:\s+(?:in|on|using|with)\s+(.+))?$"
```

This is a deliberately generous grammar. Four trigger verbs (`open`, `launch`, `pull up`, `start`), four connector words (`in`, `on`, `using`, `with`), and — crucially — the browser clause is *entirely optional*. `"open youtube"` matches with group 2 empty; `"open youtube in brave"` matches with group 2 = `"brave"`; `"launch github using chrome"` matches the same shape with different words in the same slots. One regex, both the old fixed-phrase behavior and the new browser-aware behavior, because the browser clause degrades gracefully to `None` rather than failing to match at all.

**`parse_open_request(query)`** ties it together: runs the regex, resolves the site half through `resolve_site_url()`, resolves the (possibly absent) browser half through `resolve_browser_alias()`, and returns `(url, browser_key_or_None, site_label)` — or `None` if the query doesn't match the open-verb grammar at all, in which case `classify()` falls through to the LLM intent path.

**`open_url_in_browser(url, browser=None)`** is where the parsed intent becomes an action:
- No browser specified → `webbrowser.open(url)`, the OS default. This preserves the original, simpler "just open it" behavior when no browser was named.
- Browser specified and a launcher exists for this OS → `subprocess.Popen(launcher + [url])`, i.e. it actually shells out to `chrome.exe [url]` / `brave.exe [url]` / etc.
- Browser specified but not configured for this OS, or the binary genuinely isn't found (`FileNotFoundError`), or literally anything else goes wrong → falls back to the OS default and **says so** in its return value (`"your default browser (brave wasn't found on this system)"`), which `task_open_url()` speaks back to you. You always find out what actually happened, never a silent substitution.

The net effect: this whole layer turns a single regex match plus two lookup tables into the difference between a static dictionary and something that generalizes — "pull up reddit on firefox," "launch netflix," "open example.com in edge," and "open some obscure site nobody hardcoded" all resolve through the same four functions.

### 7. Tools & the Tool Registry

```python
TOOL_REGISTRY = {
    "web_search": ToolManager.web_search,
    "read_file": ToolManager.read_file,
    "write_file": ToolManager.write_file,
    "run_shell": ToolManager.run_shell,
    "open_browser": ToolManager.open_browser,
}
```

Five callables, each taking a single string argument and returning a string observation — this uniform signature is what lets the agent loop treat every tool identically, regardless of what it actually does underneath.

| Tool | Input format | What it does |
|---|---|---|
| `web_search` | free text query | Scrapes DuckDuckGo's HTML endpoint, regex-strips markup, returns top 5 title+snippet pairs |
| `read_file` | file path | Reads up to 4000 characters, `errors="replace"` for encoding safety |
| `write_file` | `path::content` | Creates parent directories as needed, writes UTF-8 |
| `run_shell` | shell command | Runs via `subprocess.run(shell=True)`, blacklist-filtered, 20s timeout (`TOOL_TIMEOUT`), output capped at 4000 chars |
| `open_browser` | `site::browser` (browser optional) | Thin agent-facing wrapper around `resolve_site_url()` + `open_url_in_browser()` — the *same* browser intelligence described above, but callable by the LLM mid-reasoning-chain rather than only from the fast-path regex |

`open_browser` deserves a specific callout: it means the agent doesn't just get *file and shell* capabilities — it inherits the full site/browser resolution logic as a first-class tool, so a multi-step agentic goal like *"look up the trailer for the new Dune movie and open it in Brave"* can chain `web_search` into `open_browser` within a single reasoning loop, not just handle the fast-path single-command case.

**Shell safety** is a blacklist, not a sandbox:

```python
DANGEROUS_SHELL_PATTERNS = [
    r"rm\s+-rf\s+/", r"del\s+/f", r"format\s+[a-z]:", r"mkfs",
    r"diskpart", r"shutdown", r"reg\s+delete", r"cipher\s+/w",
    r"vssadmin", r"dd\s+if=",
]
```

Read this as *"catches the loudest, most obvious footguns"* rather than *"catches everything dangerous."* It is not a security boundary in the airtight sense — a sufficiently different phrasing of a destructive command, or a chained command using `&&`/`;`/`|` around a pattern-matching prefix, is not guaranteed to be caught. See [Known Limitations](#known-limitations--security-notes) below for the honest version of this conversation.

### 8. The Agent Loop (ReAct)

```python
def agent_loop(goal: str, memory_context: str = "") -> str:
```

This is the general-purpose reasoning engine — the `A` intent, reached when `classify()` can't resolve a request to a fast local pattern and the LLM's intent tag comes back `A` instead of `Y`/`E`/`D`/`N`. It implements the **ReAct** pattern (Reason + Act), a prompting technique where the model alternates between explaining its reasoning and either invoking a tool or delivering a final answer — one step at a time, with the *result* of each tool call fed back in before the next reasoning step. This is deliberately different from letting the model plan an entire multi-step sequence up front: it re-evaluates after every observation, so it can course-correct on a bad search result or a failed file read instead of committing blindly to a stale plan.

The contract, enforced by `AGENT_SYSTEM_PROMPT`, is exactly two legal response shapes:

```
Thought: <reasoning>
Action: tool_name[input]
```
or
```
Thought: <reasoning>
Final Answer: <answer>
```

Two regexes do the parsing:

```python
ACTION_REGEX = re.compile(r"Action:\s*(\w+)\[(.*)\]", re.DOTALL)
FINAL_REGEX  = re.compile(r"Final Answer:\s*(.*)", re.DOTALL)
```

The loop body, each of up to `MAX_AGENT_STEPS` (default 6) iterations:

1. Build the prompt: memory context (if any) + the goal + everything accumulated in `scratchpad` so far.
2. Call `ollama_generate()` against `MODEL_GENERAL`.
3. Check for `Final Answer:` first — if found, the loop terminates immediately and returns it.
4. Otherwise check for `Action: tool[input]` — extract the tool name and argument, look it up in `TOOL_REGISTRY`, execute it (or return `"Unknown Tool: {name}"` if the model hallucinated a tool that doesn't exist), and append the model's own response *plus* the resulting `Observation:` back onto the scratchpad for the next iteration to see.
5. If the response matches *neither* pattern — the model went off-script — the raw response is returned as-is rather than looping forever on a malformed reply.
6. If all `MAX_AGENT_STEPS` are exhausted without a `Final Answer`, the loop returns a "maximum reasoning steps reached" message with the last 1000 characters of scratchpad, so you at least see how far it got.

Every single run — successful, malformed, or exhausted — is logged via `log_agent_trace()` to `agent_log.txt`, timestamped, with the full goal and scratchpad. This is your debugging window into agent behavior: when a request doesn't do what you expected, this file is where you go to see the model's actual reasoning trace, not just the final spoken output.

**On the model choice here**: `agent_loop` currently runs on `MODEL_GENERAL` (`gemma3:4b`) rather than `MODEL_CODE` (`qwen3:8b`). This is a meaningful design decision worth being deliberate about — general-purpose instruction-tuned models vary widely in how reliably they follow a strict "always emit either `Action:` or `Final Answer:`, never anything else" format. Models specifically trained on tool-calling data (Qwen3's family is a notable example) tend to produce far more consistent, parseable output for exactly this ReAct-loop use case than models that weren't. If agent reliability ever becomes the bottleneck, this is the first knob to try turning.

### 9. Speech Engine

```python
class SpeechWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        ...
    def speak(self, text: str): ...
```

One persistent background thread, one `pyttsx4` engine instance, one `queue.Queue()`. Every call to `speak()` anywhere in the codebase pushes `(text, threading.Event())` onto that queue and blocks on the event until the dedicated TTS thread actually finishes speaking it. This is the architectural fix for a very specific, previously-observed failure: `pyttsx4`/`pyttsx3` engines on Windows can silently stop producing audio after repeated back-to-back `say()`/`runAndWait()` calls from *different* call sites or *re-initialized* engine instances. Centralizing to exactly one engine, one thread, and a strict FIFO queue eliminates that failure class entirely — there's structurally no way for two `speak()` calls to race or interleave, because they're serialized through a single consumer loop.

`get_speech_worker()` is a thread-safe lazy singleton (same double-checked-lock pattern as `_lazy_import`), so the actual `pyttsx4.init()` cost is paid once, on first use, not at import time.

### 10. Intent Classification

Five possible tags, checked in a deliberate order of cost — cheapest and most certain first:

```python
PRIORITY_LOCAL   = 0   # fast pattern match, zero LLM calls
PRIORITY_SELF    = 1   # "D" - self-description
PRIORITY_SYSTEM  = 2   # "E" - system operation
PRIORITY_GENERAL = 3   # "N" - general conversation
PRIORITY_CODE    = 4   # "Y" - code generation
PRIORITY_AGENT   = 5   # "A" - multi-step agentic task
```

`classify(query)` runs a strict waterfall:

1. `parse_open_request()` — the open/launch/pull-up/start grammar described above. If it matches, this *never touches the LLM at all* — it's resolved entirely in Python, deterministically, in microseconds.
2. `screenshot`, `time`, exit phrases (`stop`/`exit`/`quit`), bye phrases (`bye`/`good bye`/`good day`) — each a `contains_phrase()` word-boundary regex check, same zero-LLM-call principle.
3. Empty/near-empty query → `noop`, silently dropped.
4. Only if none of the above match does it fall through to `intention_checker(query)` — the one and only point where an LLM call decides intent.

`contains_phrase()` wraps every check in `\b...\b` word-boundary regex, specifically to avoid the class of bug where `"time"` matches inside an unrelated word — substring containment (`"time" in query`) is a strictly weaker, bug-prone check that this deliberately avoids.

`intention_checker()` sends the query to `MODEL_GENERAL` with `INTENT_SYSTEM_PROMPT` (temperature `0`, `max_tokens=10` — short by design, since the only valid outputs are one character) and then **scans the response in reverse** for the first character in `{Y, E, D, N, A}`:

```python
for char in reversed(response):
    if char in ["Y", "E", "D", "N", "A"]:
        return char
return "N"
```

Reverse-scanning rather than forward-scanning is a specific accommodation for smaller local models, which are more prone than large hosted models to prepend filler text before the actual answer ("Sure, the answer is: N") — the *last* matching character is far more reliably the model's actual classification than the first. If nothing matches at all, it defaults to `"N"` (general conversation) rather than crashing or leaving intent undetermined — the safest failure mode, since general conversation is always a valid (if not always maximally useful) fallback.

### 11. Priority Scheduler

```python
class PriorityScheduler:
    def __init__(self, max_workers=3):
        self.queue = queue.PriorityQueue()
        self.pending = 0
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3, ...)
        self.dispatcher = threading.Thread(target=self._dispatch_loop, daemon=True)
```

The execution core. A `queue.PriorityQueue()` naturally orders by the tuple's first element — here, `(priority, counter, function, args, kwargs)` — so lower-numbered priorities (local actions) always dequeue before higher-numbered ones (agentic tasks), and `itertools.count()` as the tiebreaker guarantees FIFO ordering *within* the same priority level (Python's tuple comparison would otherwise attempt to compare function objects on a priority tie, which either errors or produces undefined ordering).

A dedicated dispatcher thread (`_dispatch_loop`) continuously pulls from the priority queue and hands work to a bounded `ThreadPoolExecutor(max_workers=3)` — bounded specifically so that a burst of queued tasks (e.g., a compound voice command split into five sub-tasks) can't spawn unbounded threads and exhaust system resources.

**Busy-state tracking** is the mechanism that lets the main loop know whether anything is in flight, without polling task objects directly:

```python
def register_pending(self):
    with self.pending_lock:
        self.pending += 1
        became_busy = self.pending == 1
    if became_busy:
        self.state_changed.set()
    return self.pending
```

`pending` is incremented on `submit()`/`run_now()` and decremented in `_execute()`'s `finally` block — guaranteed to decrement even if the task raised an exception, so a crashing task handler can never permanently wedge the scheduler into "always busy." `state_changed` is a `threading.Event()` that fires exactly on the 0→1 and 1→0 transitions (not on every increment/decrement), giving the main loop an efficient `wait_for_state_change(timeout=1)` to block on rather than a tight polling loop.

**Thread priority** is actively deprioritized for background work on Windows:

```python
def set_current_thread_priority(level: int):
    ...
    ctypes.windll.kernel32.SetThreadPriority(handle, level)
```

Both the dispatcher thread and every executed task run at `THREAD_PRIORITY_BELOW_NORMAL`, while the *main* thread (voice capture, the responsiveness-critical path) is bumped to `THREAD_PRIORITY_ABOVE_NORMAL` at startup. This is a direct answer to "I'm talking to it while it's mid-task and the mic feels sluggish" — background LLM calls and shell executions are explicitly told by the OS scheduler to yield CPU time to the foreground voice loop, not fight it for cycles. No-op on non-Windows platforms (`IS_WINDOWS` guard), since this is a `ctypes.windll` call specific to the Win32 API.

**Speech serialization**: `speak_safe()` wraps every spoken response in `self.speak_lock`, and — if a `mic_listener` is registered — explicitly `pause()`s it before speaking and `resume()`s it in a `finally` block after. This exists to prevent the classic self-triggering bug: JARVIS hearing its own voice through the microphone and interpreting it as a new command.

### 12. Task Handlers & Dispatch

Ten task functions (`task_open_url`, `task_screenshot`, `task_time`, `task_exit`, `task_bye`, `task_system_operation`, `task_self_description`, `task_code`, `task_general`, `task_agent`), each a thin, single-purpose function that takes the `scheduler` (for `speak_safe()`) plus whatever payload it needs. `get_task(scheduler, kind, payload, query)` is the single mapping table from a `classify()`-produced `kind` string to `(function, args)` — the one place that would need editing to add a new task type.

`dispatch()` and `execute_direct()` are two entry points into the same mapping, differentiated by urgency: `dispatch()` goes through `scheduler.submit()` (the priority queue, for compound multi-task commands where ordering matters), while `execute_direct()` goes through `scheduler.run_now()` (straight to the thread pool, bypassing the queue entirely) — used specifically when a command resolves to exactly one task, where queueing overhead buys nothing.

### 13. Command Splitting

```python
def split_commands(query: str):
    if " and " in query: return query.split(" and ")
    if "." in query: return query.split(".")
    return [query]
```

Handles compound voice commands ("open youtube and take a screenshot and write a python program to sort a list") by splitting on `" and "` first, falling back to `.` for dictated-punctuation phrasing, and treating the whole query as one command if neither delimiter is present. `handle_command()` then classifies each piece independently, filters out anything that resolved to `noop`, and — if more than one real task resulted — **partitions them**: all `PRIORITY_LOCAL` tasks go first (regardless of original order), then everything else sorted by priority. This means "open youtube and write a program to reverse a string and take a screenshot" always opens the browser and fires the screenshot before it even starts waiting on the (much slower) code-generation LLM call, independent of the order you spoke them in.

### 14. Microphone Listener

```python
class MicListener:
    def __init__(self, scheduler): ...
    def listen_once(self) -> str | None: ...
```

**Calibration**: on init, `adjust_for_ambient_noise(source, duration=1)` sets an initial `energy_threshold` from one second of room noise, then it's clamped to a hard floor:

```python
if self.recognizer.energy_threshold < MIN_ENERGY_THRESHOLD:
    self.recognizer.energy_threshold = MIN_ENERGY_THRESHOLD  # 300
```

This exists because ambient-noise calibration in a genuinely quiet room can settle far too low (observed as low as `55` in practice), at which point the recognizer starts firing on breath sounds and background hiss — producing a stream of `"heard something, couldn't transcribe it"` with no real speech behind any of it. The floor at 300 (roughly SpeechRecognition's own sane default) prevents over-sensitivity regardless of how quiet the calibration moment happened to be.

**Wake word matching**: six variants (`jarvis`, `alex`, `alexa`, `alec`, `elix`, `sonu`) checked via `contains_phrase()`'s word-boundary regex — deliberately generous, because short wake words are exactly what cloud STT engines are most prone to mis-transcribe, and a mis-hear that still lands on a close variant should still trigger.

**Two-step *and* one-shot wake patterns, both supported**: this is the fix for a real observed failure where a user said "Jarvis" alone, paused, then separately said the actual command — and the original implementation only ever checked for a command *within the same utterance* as the wake word, silently discarding the wake-word-only phrase and never hearing the follow-up at all.

```python
def resolve_command(self, text):
    wake = self.find_wake_word(text)
    if wake is None: return None
    play_wake_sound()
    remaining = text.lower().split(wake, 1)[1].strip(" ,.")
    if remaining:
        return remaining          # "jarvis, open youtube" — inline, one breath
    # wake word said alone → listen again
    audio = self._listen()
    command = self._recognize(audio)
    return command.strip() if command else None
```

If there's text *after* the wake word in the same utterance, that's the command — handled in one pass. If the wake word was the entire utterance, it explicitly does a second blocking `listen()` for the follow-up, Alexa-style. Both speaking patterns now work identically.

**Full transcription is always logged** (`safe_print(f"Heard: {text}")`) regardless of whether a wake word was found — this exists specifically so a mis-hear is *visible and debuggable* rather than silently swallowed, which was previously indistinguishable from "the microphone isn't picking up audio at all."

### 15. Bootstrap & Main Loop

`initialize()` runs, in strict order: startup banner + sound → speech engine warm-up → Ollama reachability check (with both required models verified present, hard exit + spoken error if not) → `PriorityScheduler` construction → `MicListener` construction (mic calibration happens here) → greeting (`wish()`) → "JARVIS ONLINE" banner. Every stage prints a `[init]` line, so a hang or crash during startup tells you exactly which subsystem was mid-initialization.

The main loop is intentionally simple:

```python
while not shutdown_event.is_set():
    command = microphone.listen_once()
    if command:
        handle_command(scheduler, command)
    while scheduler.is_busy() and not shutdown_event.is_set():
        scheduler.wait_for_state_change(timeout=1)
```

Listen → dispatch → **wait for the scheduler to fully drain** before listening again. This is a deliberate trade-off, not an oversight: the microphone is *not* actively listening while any task is executing. The upside is architectural simplicity and a complete absence of the self-triggering/race-condition class of bugs that a concurrent "listen while busy" design invites (there's no need for the `mic.pause()`/`resume()` calls in `speak_safe()` to coordinate against a simultaneously-active background listener, because there isn't one). The trade-off is that you cannot currently barge in with a new command while JARVIS is still finishing the last one — if that becomes a real friction point in practice, the extension point is exactly here, swapping `listen_once()` for a `listen_in_background()`-based path gated on `scheduler.is_busy()`.

`shutdown_event` (a plain `threading.Event()`) is the single global stop signal — set by `task_exit()`, checked by both loop conditions above. Teardown in `finally` plays the shutdown sound, calls `scheduler.shutdown(wait=False)` (doesn't block waiting for in-flight tasks to finish — a deliberate choice for responsive exit over graceful drain), and calls `os._exit(0)` rather than a plain `sys.exit()` — a hard process termination that guarantees no lingering non-daemon thread (there shouldn't be any, but this is the belt-and-suspenders version) can keep the interpreter alive after you've asked it to stop.

---

## Full Trace: "Jarvis, open YouTube in Brave"

Every function this single sentence actually passes through, in order:

1. **`MicListener.listen_once()`** — blocking `recognizer.listen()`, captures audio.
2. **`_recognize()`** — Google STT via `recognize_google(language="en-in")` → `"jarvis open youtube in brave"`. Logged: `Heard: jarvis open youtube in brave`.
3. **`find_wake_word()`** — matches `"jarvis"`.
4. **`resolve_command()`** — wake word found *with* remaining text in the same utterance → `play_wake_sound()` fires, returns `"open youtube in brave"` directly. No second listen needed.
5. **`handle_command(scheduler, "open youtube in brave")`** — logs `[dispatch] open youtube in brave`.
6. **`split_commands()`** — no `" and "`, no `.` → single-item list, unchanged.
7. **`classify("open youtube in brave")`**:
   - `parse_open_request()` matches `OPEN_PATTERN`: verb=`"open"`, site=`"youtube"`, browser clause=`"brave"`.
   - `resolve_site_url("youtube")` → exact hit in `SITE_SHORTCUTS` → `"https://youtube.com"`.
   - `resolve_browser_alias("brave")` → exact hit in `BROWSER_ALIASES` → `"brave"`.
   - Returns `(PRIORITY_LOCAL, "open", ("https://youtube.com", "brave", "youtube"))`. **No LLM call made at any point in this step.**
8. **`handle_command`** sees exactly one classified task → **`execute_direct()`** → `scheduler.run_now(task_open_url, scheduler, action)` — bypasses the priority queue entirely, straight to the thread pool.
9. **`task_open_url(scheduler, action)`** unpacks `(url, browser, label)`, calls **`open_url_in_browser("https://youtube.com", "brave")`**.
10. `get_platform_key()` → `"win32"` (say). `BROWSER_LAUNCHERS["win32"]["brave"]` → `["brave.exe"]`. `subprocess.Popen(["brave.exe", "https://youtube.com"])` launches. Returns `"brave"`.
11. **`scheduler.speak_safe("Opening youtube in brave.")`** — acquires `speak_lock`, pauses the mic listener, pushes the text onto `SpeechWorker`'s queue, blocks until the dedicated TTS thread finishes speaking it, resumes the mic listener.
12. **`task_completed()`** decrements `pending` back to 0, fires `state_changed`.
13. Main loop's `wait_for_state_change()` wakes up, sees `is_busy() == False`, exits the inner wait loop, calls `listen_once()` again — ready for the next command.

Thirteen steps, zero LLM calls, sub-second wall-clock time for everything except the STT round-trip and the TTS playback itself. This is the entire point of resolving `open`-shaped requests deterministically in Python rather than routing them through `intention_checker()` and the general chat model — it's not just more reliable, it's dramatically faster.

---

## Output Files

| File | Written by | Contents |
|---|---|---|
| `memory.json` | `Memory._save()` | Persistent long-term summary + recent raw turns |
| `generated_code.txt` | `task_code()` | Every code-generation response, timestamped, appended |
| `response.txt` | `task_general()` | Every general-chat response, timestamped, appended |
| `commands.txt` | `task_system_operation()` | Every system-operation response, overwritten each time |
| `agentic_response.txt` | `task_agent()` | Every agent final answer, timestamped, appended |
| `agent_log.txt` | `log_agent_trace()` | Full ReAct scratchpad (every Thought/Action/Observation) for every agent run, success or failure |
| `screenShots/screenshot_<timestamp>.png` | `task_screenshot()` | Timestamped screenshots |

`agent_log.txt` is the one to open first when an agentic task didn't do what you expected — it's the complete, unfiltered reasoning trace, not just the spoken summary.

---

## Known Limitations & Security Notes

Said plainly, because a project this deliberate deserves an equally honest accounting of where it isn't:

- **`run_shell`'s blacklist is not a sandbox.** `DANGEROUS_SHELL_PATTERNS` catches the loudest, most obvious destructive commands (`rm -rf /`, `format c:`, `diskpart`, ...) but is not exhaustive — a differently-phrased destructive command, a chained command (`&&`, `;`, `|`) around an otherwise-benign-looking prefix, or a PowerShell-native equivalent (`Remove-Item -Recurse -Force`) is not guaranteed to be caught. The trigger path is voice → LLM interpretation → shell execution, with no confirmation step in between — a misheard command or a hallucinated flag has a real, if narrow, path to unintended action. If this matters for your use, the more robust pattern is an *allowlist* of specific safe commands rather than a blacklist of dangerous ones.
- **`write_file` has no path sandboxing.** It accepts whatever path the model's tool call specifies and writes there, anywhere the OS process has permission to write. Consider constraining it to a fixed base directory (resolve the path, reject anything that escapes it) if the agent will ever run with elevated or broad filesystem permissions.
- **The agent loop has no wall-clock ceiling**, only a step ceiling (`MAX_AGENT_STEPS = 6`). Worst case is `6 × (LLM latency + tool timeout)`, which for a local 4B model plus a 20-second shell timeout can genuinely stretch into minutes — long for something meant to feel like a responsive voice interaction.
- **The mic is fully silent while any task is executing** (see [Bootstrap & Main Loop](#15-bootstrap--main-loop)) — no barge-in support currently. Deliberate trade-off for simplicity and race-condition avoidance, not an oversight, but worth knowing if you expect Alexa-style interruptibility.
- **`gemma3:4b` driving the agent loop's tool selection** is a smaller, more general model than a tool-calling-specialized one — expect occasional malformed `Action:` lines or missed tool opportunities on ambiguous multi-step goals. `agent_log.txt` will show you exactly when and how.

---

## Troubleshooting

**"Wake word isn't being heard at all"**
Check the console for `Heard: ...` lines. If nothing is being transcribed at all, it's a microphone/calibration issue — check `energy_threshold` in the `[mic] Ready` log line; if it seems too low or too high for your room, that's `MIN_ENERGY_THRESHOLD` to tune. If transcriptions *are* appearing but never match a wake word, check the actual transcribed text against `WAKE_WORDS` — Indian-English STT (`language="en-in"`) can transcribe short words unpredictably.

**`Couldn't connect to Ollama at http://localhost:11434`**
`ollama serve` isn't running, or something else already owns port 11434 (`netstat -ano | findstr :11434` on Windows to check). If the desktop tray app is already running Ollama in the background, you don't need a second `ollama serve` — the existing instance is already serving requests.

**`{model} not found`**
`ollama pull gemma3:4b` / `ollama pull qwen3:8b` — `initialize()` checks `ollama list`-equivalent output against `CONFIG["MODEL_GENERAL"]`/`CONFIG["MODEL_CODE"]` exactly, so the pulled tag has to match the config string precisely.

**`UnicodeEncodeError` / `'charmap' codec can't encode character`**
Should not occur given the encoding-safety layer described above — if it does, it means some code path is writing to a file or stream that bypassed `safe_write()`/`safe_print()`. Worth a `grep` for any stray `open(...)` or `print(...)` that isn't calling through those wrappers.

**TTS goes silent after the first sentence**
Should not occur given the single-worker-thread `SpeechWorker` design — this was the exact failure mode it was built to eliminate. If it recurs, check whether something outside this file is calling `pyttsx4` directly rather than through `speak()`.

---

## Roadmap

Toward "wake up, Daddy's home" — not there yet, but every subsystem above is a deliberate step in that direction:

- [ ] Barge-in support: background mic listening during active task execution, gated on `scheduler.is_busy()`.
- [ ] Allowlist-based `run_shell`, replacing the current blacklist.
- [ ] Path-sandboxed `write_file`.
- [ ] Wall-clock ceiling on `agent_loop`, independent of step count.
- [ ] Tool-calling-specialized model for the agent's reasoning step, evaluated against the current `gemma3:4b` baseline.
- [ ] Persistent per-user voice profile / speaker identification (the original, long-abandoned `extract_features()`/`KNeighborsClassifier` scaffolding in early versions of this project).
- [ ] Wake-word detection running fully offline (no cloud STT round-trip for the trigger phrase itself).
