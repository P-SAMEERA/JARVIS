<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS — README</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
:root{
  --bg:#0B121C;
  --bg-panel:#111A28;
  --line:rgba(148,183,222,0.12);
  --accent:#38BDF8;
  --text-0:#E8EEF6;
  --text-1:#AEBBCC;
  --text-2:#6E7C90;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,sans-serif;
}
*{box-sizing:border-box;}
body{
  margin:0;
  background:var(--bg);
  color:var(--text-1);
  font-family:var(--sans);
  font-size:16px;
  line-height:1.7;
}
a{color:var(--accent);}

#shell{
  display:grid;
  grid-template-columns:260px minmax(0,1fr);
  max-width:1180px;
  margin:0 auto;
}
#sidebar{
  position:sticky;
  top:0;
  height:100vh;
  overflow-y:auto;
  padding:28px 14px 40px 20px;
  border-right:1px solid var(--line);
}
#sidebar a{
  display:block;
  padding:5px 10px;
  border-radius:6px;
  color:var(--text-2);
  font-size:13px;
  text-decoration:none;
}
#sidebar a:hover{color:var(--text-0); background:var(--bg-panel);}
#sidebar .h1-link{color:var(--text-1); font-weight:600; font-size:13.5px; margin-top:6px;}
#sidebar .h2-link{padding-left:20px;}
#sidebar a.active{color:var(--accent); font-weight:600;}

#content{
  min-width:0;
  padding:40px 48px 120px;
  max-width:760px;
}

.md-heading{scroll-margin-top:24px; color:var(--text-0); display:flex; align-items:center; gap:8px;}
h1.md-heading{font-size:26px; margin:44px 0 16px;}
h2.md-heading{font-size:19px; margin:34px 0 10px;}
h3.md-heading{font-size:15px; margin:24px 0 8px; color:var(--text-1);}
.collapse-btn{
  margin-left:auto; background:none; border:none; color:var(--text-2);
  cursor:pointer; font-size:12px; opacity:0; transition:opacity .15s;
}
.md-heading:hover .collapse-btn{opacity:1;}
.collapse-btn.collapsed{transform:rotate(-90deg);}

#content p{margin:0 0 15px; color:var(--text-1);}
#content strong{color:var(--text-0);}
#content ul,#content ol{margin:0 0 15px; padding-left:22px;}
#content li{margin-bottom:5px;}
#content li::marker{color:var(--accent);}
#content hr{border:none; border-top:1px solid var(--line); margin:32px 0;}
#content [data-collapsed="true"]{display:none;}

#content :not(pre) > code{
  font-family:var(--mono); font-size:0.86em;
  background:var(--bg-panel); border:1px solid var(--line);
  color:var(--accent); padding:1.5px 6px; border-radius:5px;
}

.table-wrap{overflow-x:auto; margin:0 0 18px; border:1px solid var(--line); border-radius:8px;}
table{border-collapse:collapse; width:100%; font-size:13.5px;}
th{text-align:left; background:var(--bg-panel); padding:9px 12px; border-bottom:1px solid var(--line); color:var(--text-0);}
td{padding:9px 12px; border-bottom:1px solid var(--line);}
tr:last-child td{border-bottom:none;}

blockquote{
  margin:0 0 18px; padding:10px 16px;
  border-left:3px solid var(--accent);
  background:var(--bg-panel);
  border-radius:0 8px 8px 0;
  color:var(--text-1);
}
blockquote p{margin:0;}

.code-window{margin:0 0 18px; border:1px solid var(--line); border-radius:8px; overflow:hidden; background:#0A1220;}
.code-header{display:flex; align-items:center; gap:8px; padding:7px 12px; background:var(--bg-panel); border-bottom:1px solid var(--line);}
.lang{font-family:var(--mono); font-size:10.5px; color:var(--text-2); text-transform:uppercase;}
.copy-btn{
  margin-left:auto; background:transparent; border:1px solid var(--line);
  color:var(--text-2); font-size:11px; padding:3px 8px; border-radius:5px; cursor:pointer;
}
.copy-btn:hover{color:var(--accent); border-color:var(--accent);}
.copy-btn.copied{color:#34D399; border-color:#34D399;}
pre{margin:0; padding:14px 16px; overflow-x:auto;}
code{font-family:var(--mono); font-size:13px; color:var(--text-1);}

.hljs-keyword,.hljs-literal,.hljs-section{color:var(--accent);}
.hljs-string,.hljs-title{color:#7EE8B0;}
.hljs-number{color:#F0A868;}
.hljs-comment{color:var(--text-2); font-style:italic;}
.hljs-attr,.hljs-built_in,.hljs-variable{color:#9AB8FF;}

#toggle{
  display:none;
  position:fixed; top:14px; left:14px; z-index:50;
  background:var(--bg-panel); border:1px solid var(--line); color:var(--text-1);
  width:36px; height:36px; border-radius:8px; cursor:pointer;
}
@media (max-width:800px){
  #shell{grid-template-columns:1fr;}
  #sidebar{position:fixed; top:0; left:0; bottom:0; width:78vw; max-width:300px;
    background:var(--bg); z-index:40; transform:translateX(-100%); transition:transform .2s;}
  #sidebar.open{transform:translateX(0);}
  #content{padding:70px 20px 100px;}
  #toggle{display:block;}
}
</style>
</head>
<body>

<button id="toggle">☰</button>
<div id="shell">
  <aside id="sidebar"><nav id="toc"></nav></aside>
  <main id="content"></main>
</div>

<textarea id="readme-source" style="display:none"># JARVIS

### A local, voice-driven, modular AI assistant that runs entirely on your machine.

> "Wake up. Daddy's home."

No cloud API keys.

No per-token billing.

No subscription services.

No data leaving your machine.

Just you, a microphone, two locally-running Ollama models, a priority-based execution engine, and a modular architecture designed to grow from a voice assistant into a complete local AI operating system.

---

This document exists because software eventually outlives the memory of the person who wrote it.

Code explains *what* happens.

Architecture explains *why* it happens.

JARVIS has gone through multiple generations. Earlier versions worked, but everything lived inside a single monolithic `AI.py` file. That design was sufficient while the assistant could only answer questions or perform a handful of local actions.

It eventually became impossible to reason about.

Every new feature touched multiple unrelated sections of the same file.

Speech logic lived beside browser automation.

The scheduler knew about microphone state.

Intent classification lived beside initialization code.

Agent reasoning lived beside startup banners.

Nothing was technically broken.

Everything was becoming increasingly difficult to maintain.

The project was therefore redesigned around a simple principle:

> **Each module should own one responsibility, and only one responsibility.**

The result is no longer "a Python script."

It is now a collection of independent subsystems that cooperate to behave like one assistant.

Each subsystem has clear ownership.

Each module exposes a small public API.

Dependencies flow in one direction.

Features can evolve independently.

Understanding the project no longer requires reading thousands of lines from top to bottom.

Instead, understanding JARVIS is understanding how information flows through the system.

This document follows exactly that journey.

---

# Table of Contents

1. Philosophy
2. Evolution of the Architecture
3. Project Structure
4. Architecture Overview
5. Installation
6. Configuration Reference
7. Subsystem Deep Dive

   1. Bootstrap
   2. Main Loop
   3. Scheduler
   4. Speech Engine
   5. Microphone Listener
   6. Command Processor
   7. Intent Classification
   8. Dispatcher
   9. Task Handlers
   10. Browser Resolution
   11. Persistent Memory
   12. Ollama Client
   13. Agent Loop (ReAct)
   14. Tool Registry
   15. Sound Manager
   16. Helpers & Utilities

8. Complete Execution Trace
9. Output Files
10. Design Decisions
11. Threading Model
12. Known Limitations
13. Troubleshooting
14. Future Roadmap

---

# Philosophy

Most "AI Assistant" tutorials follow a surprisingly similar pattern.

A wake word is detected.

Speech is converted to text.

The text is sent to a language model.

The model produces a response.

The response is spoken back.

That architecture produces something that can talk.

It does **not** produce something that can reliably act.

A language model is exceptionally good at understanding language.

It is comparatively poor at deterministic execution.

If you ask a model to:

> "Open YouTube in Brave."

you don't actually want creativity.

You want correctness.

There should be exactly one browser.

Exactly one URL.

Exactly one execution path.

No hallucination.

No interpretation.

No guessing.

That observation shaped the entire architecture.

JARVIS separates intelligence from execution.

The LLM understands.

Python executes.

Those are fundamentally different responsibilities.

Whenever a task can be solved deterministically, it is solved deterministically.

Only genuinely ambiguous requests are delegated to an AI model.

That philosophy appears repeatedly throughout the project.

Examples include:

- Browser requests never require an LLM.
- Screenshots never require an LLM.
- Time queries never require an LLM.
- Exit commands never require an LLM.
- Wake-word detection never requires an LLM.

The language model exists only where language itself must be understood.

Everything else is deterministic Python.

This single design decision dramatically reduces latency, increases reliability, and makes debugging practical.

---

# Evolution of the Architecture

The first versions of JARVIS consisted almost entirely of one file.

```

AI.py
│
├── Speech
├── Memory
├── Scheduler
├── Browser
├── Agent
├── Microphone
├── Sound
├── Intent Classification
├── Task Dispatch
├── Startup
└── Main Loop

```

Nothing prevented this architecture from working.

But every new feature increased coupling.

A modification to one subsystem frequently required editing code belonging to several others.

The file eventually became thousands of lines long.

That wasn't merely inconvenient.

It was a warning.

Large files are not inherently bad.

Large files containing **multiple unrelated responsibilities** are.

The solution was not to split code randomly.

The solution was to identify ownership.

Each subsystem became its own module.

Initialization became `bootstrap.py`.

Speech became `speech.py`.

Scheduling became `scheduler.py`.

Command parsing became `command_processor.py`.

Intent classification became `ai/classifier.py`.

Browser intelligence became `browser.py`.

The agent became its own package under `ai/`.

The result is a codebase whose architecture now mirrors the runtime itself.

Each module answers one question.

Nothing more.

Nothing less.

```
main.py
        │
        ▼
bootstrap.py
        │
        ▼
microphone.py
        │
        ▼
command_processor.py
        │
        ▼
ai/classifier.py
        │
        ▼
dispatcher.py
        │
        ▼
scheduler.py
        │
        ▼
tasks.py
```

Each layer only depends on the layer beneath it.

That simple rule is what makes the project maintainable.

---

# Project Structure

```text
jarvis/
│
├── main.py                     # Entry point
├── bootstrap.py                # System initialization
├── config.py                   # Global configuration
├── helpers.py                  # Shared helper functions
├── browser.py                  # Browser and URL resolution
├── memory.py                   # Persistent conversation memory
├── microphone.py               # Voice capture and wake-word detection
├── scheduler.py                # Priority-based task scheduler
├── speech.py                   # Text-to-speech engine
├── dispatcher.py               # Task routing
├── command_processor.py        # Command splitting and orchestration
├── tasks.py                    # Task implementations
├── tools.py                    # Agent tool registry
├── sound.py                    # Notification sounds
├── utils.py                    # Shared utility helpers
│
├── ai/
│   ├── __init__.py
│   ├── client.py               # Ollama communication
│   ├── classifier.py           # Intent routing
│   ├── parser.py               # ReAct parser
│   ├── prompts.py              # AI system prompts
│   └── agent.py                # ReAct agent loop
│
├── assets/
│
├── memory.json
├── commands.txt
├── response.txt
├── generated_code.txt
├── agent_log.txt
└── README.md
```

Unlike the original monolithic design, this folder structure reflects execution boundaries rather than arbitrary code organization.

Each file owns one subsystem.

No subsystem needs to understand the internal implementation of another.

This separation allows JARVIS to continue growing without requiring another architectural rewrite.

---

# Architecture at a Glance

```
                           Microphone
                                │
                                ▼
                      MicListener.listen_once()
                                │
                                ▼
                    command_processor.handle_command()
                                │
                                ▼
                     ai.classifier.classify()
                                │
               ┌────────────────┴─────────────────┐
               │                                  │
      Deterministic Task                 AI Classification
               │                                  │
               └────────────────┬─────────────────┘
                                ▼
                        dispatcher.dispatch()
                                │
                                ▼
                      PriorityScheduler
                                │
         ┌──────────────┬───────────────┬──────────────┐
         ▼              ▼               ▼              ▼
    Browser        General AI       Code AI       Agent Loop
         │              │               │              │
         ▼              ▼               ▼              ▼
     Speech Queue   Ollama        Ollama         Tool Registry
                               
```

Unlike previous versions, every box in this diagram corresponds to an actual Python module.

Understanding the architecture therefore becomes significantly easier.

The execution flow of the assistant and the folder structure are now almost identical.

# Installation

JARVIS is designed to run entirely on a local machine.

Inference, scheduling, speech synthesis, memory, browser automation and tool execution all happen locally.

The only external dependency required for inference is an Ollama server running on the same machine.

No API keys are required.

No internet connection is required after the required models have been downloaded (except for features that intentionally access the web).

---

## 1. Install Ollama

Download Ollama from:

https://ollama.com/

After installation, pull the models required by JARVIS.

```bash
ollama pull gemma3:4b
ollama pull qwen3:8b
```

These two models serve completely different purposes.

| Model | Responsibility |
|--------|----------------|
| `gemma3:4b` | Intent classification, conversation, memory summarization and agent reasoning |
| `qwen3:8b` | Code generation |

Separating responsibilities between models allows each one to specialize.

General reasoning and code generation have very different prompting requirements.

Rather than forcing one model to do both, JARVIS delegates each task to the model that performs it best.

---

## 2. Start Ollama

```bash
ollama serve
```

Before JARVIS finishes booting, `bootstrap.initialize()` verifies three things.

1. Ollama is reachable.

2. Both configured models exist.

3. The server is responding correctly.

If any of these checks fail, startup stops immediately.

This is intentional.

A startup failure is significantly easier to debug than discovering ten minutes later that code generation silently cannot work because one model was never downloaded.

---

## 3. Install Python Dependencies

```bash
pip install requests
pip install SpeechRecognition
pip install pyttsx4
pip install pyaudio
pip install pyautogui
pip install pydub
```

Some libraries are intentionally imported lazily.

For example, if notification sounds are never played, `pydub` is never imported.

This reduces startup time while allowing optional functionality to degrade gracefully.

---

## 4. Configure Assets

Populate the `assets/` directory with the sound files referenced by `config.py`.

Typical sounds include:

- Wake
- Screenshot
- Startup
- Shutdown
- Success
- Error

Unlike many applications, missing sound files are not considered fatal.

The sound subsystem simply checks whether a file exists before attempting playback.

If a sound is unavailable, execution continues silently.

The assistant should never fail simply because a notification sound could not be played.

---

## 5. Run

After all dependencies are installed:

```bash
python main.py
```

Unlike previous versions of the project, execution now begins inside `main.py`.

`main.py` intentionally contains almost no application logic.

Its responsibility is orchestration.

All initialization happens elsewhere.

---

# Configuration Reference

Every configurable parameter in the entire project lives inside `config.py`.

Nothing else hardcodes model names, paths, URLs or runtime constants.

This centralization serves two purposes.

First, configuration becomes discoverable.

Second, every subsystem can import only the values it requires instead of depending on unrelated constants.

Examples include:

```python
OLLAMA_HOST

MODEL_GENERAL

MODEL_CODE

VOICE_INDEX

MEMORY_FILE

MEMORY_MAX_RAW_TURNS

MAX_AGENT_STEPS

TOOL_TIMEOUT

CODE_OUTPUT

CHAT_OUTPUT

COMMAND_OUTPUT

AGENT_OUTPUT

AGENT_LOG

SCREENSHOT_DIR

SOUNDS
```

Rather than importing one massive configuration object everywhere, each module imports only the constants it actually needs.

For example:

```
speech.py
```

needs only

```
VOICE_INDEX
```

while

```
memory.py
```

only requires

```
MEMORY_FILE

MEMORY_MAX_RAW_TURNS
```

and

```
ai/client.py
```

only depends upon

```
OLLAMA_HOST
```

This greatly reduces coupling between modules.

Changing the memory subsystem, for example, cannot accidentally affect browser logic because they share no unnecessary configuration.

---

# Subsystem Deep Dive

The following sections describe every subsystem in the order they participate during execution.

This ordering is intentional.

Reading these sections from top to bottom is equivalent to watching JARVIS boot and process a command.

---

# 1. Bootstrap

```
bootstrap.py
```

The first significant piece of code executed by the application is not the microphone.

It is not the scheduler.

It is not even the speech engine.

Everything begins inside

```
initialize()
```

Earlier versions scattered startup logic throughout `AI.py`.

Banner printing lived beside speech initialization.

Ollama verification appeared hundreds of lines away.

Scheduler construction occurred independently from microphone construction.

Startup gradually became difficult to reason about because there was no obvious "beginning."

`bootstrap.py` exists to solve exactly that problem.

It owns the entire startup lifecycle.

Nothing else initializes global services.

Its responsibilities are intentionally limited to:

- Display startup banner
- Play startup sound
- Initialize speech
- Verify Ollama
- Verify installed models
- Construct scheduler
- Construct microphone
- Connect scheduler and microphone
- Speak greeting
- Return initialized objects

No command processing occurs here.

No task execution occurs here.

No classification occurs here.

Its only purpose is preparing the runtime environment.

The startup sequence therefore becomes deterministic.

```
initialize()

↓

Startup Banner

↓

Startup Sound

↓

Speech Initialization

↓

Ollama Verification

↓

Model Verification

↓

PriorityScheduler()

↓

MicListener()

↓

wish()

↓

Return scheduler + microphone
```

Each stage logs its progress.

If startup ever fails, the exact subsystem responsible is immediately visible.

There is no ambiguity about which initialization step caused the failure.

---

## Why Bootstrap Exists

Separating initialization from execution provides several architectural advantages.

First, testing becomes easier.

A future unit test can initialize the scheduler without needing to launch the microphone.

Likewise, a GUI application can reuse the exact same initialization process.

An Electron frontend, for example, could simply call

```
initialize()
```

without duplicating startup logic.

Second, startup becomes self-documenting.

Instead of searching a thousand-line file to determine what happens before the first command is heard, every initialization step now exists inside one module.

This module has exactly one responsibility.

Preparing JARVIS for operation.

Nothing more.

---

# 2. Main Loop

```
main.py
```

If `bootstrap.py` prepares the assistant,

`main.py` drives it.

Unlike earlier versions, this file intentionally contains very little logic.

Its purpose is orchestration rather than implementation.

The overall flow is remarkably simple.

```
Set thread priority

↓

initialize()

↓

while running

↓

listen_once()

↓

handle_command()

↓

wait until scheduler becomes idle

↓

repeat
```

The application loop itself performs almost no computation.

Instead, it coordinates independently designed subsystems.

This is one of the primary architectural improvements introduced during the refactor.

Rather than one file performing every task,

each subsystem now performs exactly one task while `main.py` simply coordinates them.

This dramatically improves readability.

A developer reading `main.py` should immediately understand the life cycle of the assistant without needing to understand browser resolution, memory compression or AI prompting.

---

## Shutdown

Shutdown is handled using a single shared synchronization primitive.

```
shutdown_event
```

Any subsystem capable of terminating the assistant simply sets this event.

The main loop observes it.

The scheduler observes it.

Once set, execution naturally exits.

During shutdown:

- Shutdown sound plays
- Scheduler stops accepting work
- Speech engine terminates
- Threads are cleaned up
- Process exits

Centralizing shutdown around one shared event avoids the complexity of passing "stop" messages through multiple independent queues.

Every subsystem agrees upon one signal.

That agreement keeps shutdown deterministic.

# 3. Priority Scheduler

```
scheduler.py
```

The scheduler is the execution engine of JARVIS.

Every action performed by the assistant ultimately passes through this subsystem.

Unlike earlier versions where commands were executed immediately after classification, the modular architecture introduces a dedicated scheduling layer between understanding a request and executing it.

This separation serves several purposes.

First, it decouples command processing from task execution.

Second, it allows multiple commands to be prioritized.

Third, it creates a single execution model shared by every subsystem.

Rather than every module spawning its own threads, all execution flows through one scheduler.

This dramatically simplifies concurrency throughout the project.

---

## Core Components

The scheduler is composed of four major components.

```
PriorityQueue

↓

Dispatcher Thread

↓

ThreadPoolExecutor

↓

Task Functions
```

Each serves a completely different responsibility.

### PriorityQueue

Incoming work is never executed immediately.

Instead, each task is represented as

```
(priority,
 counter,
 function,
 args,
 kwargs)
```

The priority queue always executes the lowest numerical priority first.

```
0

↓

1

↓

2

↓

3

↓

4

↓

5
```

where

```
0
```

represents deterministic local actions,

while

```
5
```

represents the most computationally expensive AI agent tasks.

This means opening a browser never waits behind a multi-step reasoning loop.

The assistant always feels responsive because inexpensive actions naturally execute before expensive ones.

---

## FIFO Ordering

One subtle issue arises when two tasks have identical priority.

Python's `PriorityQueue` compares tuple elements in order.

If two priorities are equal, Python attempts to compare the next element.

Function objects cannot be compared.

Without intervention, this eventually raises an exception.

The solution is surprisingly elegant.

Each submitted task receives a monotonically increasing counter.

```
(priority,
 counter,
 function,
 ...)
```

The counter guarantees deterministic FIFO ordering within the same priority level.

Tasks submitted first are executed first.

Always.

Regardless of thread timing.

---

## Dispatcher Thread

The scheduler contains one permanent dispatcher thread.

Its only responsibility is watching the priority queue.

```
PriorityQueue

↓

Dispatcher Thread

↓

Executor.submit(...)
```

The dispatcher itself performs no work.

It merely transfers tasks from the queue into the worker pool.

Separating queue management from execution keeps scheduling deterministic while allowing workers to remain fully occupied.

---

## Thread Pool

Actual work executes inside a bounded `ThreadPoolExecutor`.

```
ThreadPoolExecutor(
    max_workers=3
)
```

A bounded pool prevents thread explosion.

Imagine a command such as

> "Open YouTube and take a screenshot and tell me the time and write a sorting program."

Without a bounded executor, every task could create another thread.

Repeated commands would eventually exhaust system resources.

The fixed-size worker pool provides a hard upper limit.

No matter how many tasks are queued, only a small number execute simultaneously.

Everything else waits its turn.

---

## Busy-State Tracking

The scheduler continuously tracks whether work is currently executing.

Internally this is represented using a simple integer.

```
pending
```

Whenever work is submitted

```
pending += 1
```

Whenever work finishes

```
pending -= 1
```

Importantly,

the decrement occurs inside a `finally` block.

Even if a task crashes,

the scheduler never permanently believes it is busy.

This seemingly small implementation detail prevents an entire class of deadlocks.

---

## State Change Notification

Rather than continuously polling

```
is_busy()
```

the scheduler exposes an event indicating that its state has changed.

Transitions

```
0 → 1
```

and

```
1 → 0
```

trigger this event.

The main loop therefore sleeps efficiently until work begins or ends instead of constantly checking scheduler state.

This dramatically reduces unnecessary CPU usage while keeping responsiveness high.

---

## Thread Priority

Windows allows thread priorities to be adjusted through the Win32 API.

JARVIS takes advantage of this.

The main thread,

responsible for voice interaction,

runs above normal priority.

Worker threads execute below normal priority.

```
Main Thread

Above Normal

↓

Worker Threads

Below Normal
```

This decision is based entirely on perceived responsiveness.

The user should always be able to finish speaking without background AI tasks competing aggressively for CPU time.

On non-Windows platforms this optimization simply becomes a no-op.

The architecture remains portable.

---

## Speech Coordination

One of the scheduler's responsibilities is preventing JARVIS from hearing itself.

Before speaking,

the scheduler pauses the microphone.

```
pause()

↓

speak()

↓

resume()
```

This coordination prevents the assistant from interpreting its own synthesized speech as another voice command.

The pause/resume mechanism is deliberately placed inside the scheduler rather than the speech engine because only the scheduler has visibility into both systems simultaneously.

That separation preserves the independence of each subsystem.

---

# 4. Speech Engine

```
speech.py
```

Text-to-speech appears deceptively simple.

Call

```
engine.say()

engine.runAndWait()
```

and audio plays.

Unfortunately,

real-world behavior is considerably less reliable.

Earlier versions of JARVIS occasionally encountered a particularly frustrating issue.

Speech would work correctly.

Then randomly stop.

Restarting the application fixed it.

Nothing obvious had changed.

The underlying cause was repeated initialization of multiple speech engines from different locations.

Rather than treating speech as a function,

JARVIS treats it as a service.

---

## Single Speech Worker

Only one speech engine exists.

Ever.

```
SpeechWorker

↓

Queue

↓

Dedicated Thread

↓

pyttsx4
```

Every module communicates with the worker using the same interface.

```
speak(text)
```

No subsystem interacts with `pyttsx4` directly.

This centralization completely eliminates competing engine instances.

---

## Queue-Based Design

Speech requests are queued.

```
Task

↓

Queue

↓

Speech Thread

↓

Audio
```

Only one sentence is spoken at a time.

No overlapping voices.

No race conditions.

No competing engine calls.

The queue naturally serializes speech without requiring every subsystem to understand thread synchronization.

---

## Lazy Initialization

Speech is initialized only once.

During startup,

`bootstrap.initialize()` requests the speech worker.

If it already exists,

the existing instance is returned.

Otherwise,

a new worker is created.

Subsequent calls reuse the same worker.

The initialization cost is therefore paid exactly once during the application's lifetime.

---

## Why Not Call pyttsx4 Everywhere?

Because every additional initialization introduces another possible failure.

The speech subsystem deliberately hides the underlying engine.

Every other module depends only upon

```
speak()
```

not

```
pyttsx4
```

This abstraction makes future replacement significantly easier.

The implementation could switch to Piper,

Coqui,

Windows SAPI,

or any other TTS engine without changing a single task handler.

Only `speech.py` would require modification.

---

# 5. Microphone Listener

```
microphone.py
```

If the scheduler is the execution engine,

the microphone is the entry point into the entire system.

Every interaction begins here.

Its responsibilities are intentionally narrow.

- Listen for speech.
- Convert speech to text.
- Detect wake words.
- Return the extracted command.

Nothing more.

It performs no classification.

No execution.

No AI reasoning.

Those responsibilities belong elsewhere.

---

## Ambient Noise Calibration

Immediately after construction,

the recognizer performs ambient noise calibration.

```
adjust_for_ambient_noise()
```

This estimates background noise inside the room.

Unfortunately,

an extremely quiet environment can produce thresholds that are too low.

In practice,

values below roughly

```
300
```

were observed to trigger on breathing,

keyboard presses,

or faint electrical noise.

To prevent this,

JARVIS enforces a minimum threshold.

If calibration returns a smaller value,

the threshold is raised automatically.

This produces significantly more stable wake-word detection across different environments.

---

## Wake Words

JARVIS intentionally recognizes multiple wake words.

```
Jarvis

Alexa

Alex

Alec

Elix

Sonu
```

Cloud speech recognition is imperfect.

Especially for short names.

Allowing several phonetically similar alternatives dramatically improves real-world usability without requiring an entirely separate wake-word model.

---

## One-Shot Commands

The simplest interaction pattern is

> "Jarvis, open YouTube."

The microphone detects the wake word.

Everything after the wake word becomes the command.

```
Jarvis

↓

open youtube
```

No second listening phase is required.

The command proceeds directly into the command processor.

---

## Two-Step Conversations

Earlier versions failed whenever the user spoke

> "Jarvis."

...

> "Open YouTube."

The first utterance contained only the wake word.

No command followed.

The assistant simply returned to waiting.

This behavior felt unnatural.

Users frequently pause after saying a wake word.

The microphone now supports both interaction styles.

If speech follows the wake word in the same utterance,

that text becomes the command.

Otherwise,

the assistant performs a second blocking listen and waits specifically for the follow-up command.

Both interaction styles therefore behave identically.

The wake word serves only to activate the assistant,

not to dictate how the user must speak.

---

## Logging

Every transcription is printed.

Even unsuccessful ones.

```
Heard:

...
```

This decision greatly simplifies debugging.

Without transcription logs,

there is no practical way to distinguish

- microphone failure,
- speech-recognition failure,
- wake-word mismatch,
- or command-processing failure.

Logging the recognized text makes the entire input pipeline observable.

That visibility has proven invaluable while developing the assistant.

# 6. Command Processor

```
command_processor.py
```

The microphone returns text.

Nothing more.

It does not know whether the text is asking for a screenshot.

It does not know whether the user wants code.

It does not know whether the request should be handled by an AI model.

Its only responsibility is converting speech into text.

From this point onward, responsibility shifts entirely to the command processor.

This module acts as the bridge between raw language and executable tasks.

Unlike earlier versions, where command parsing, intent detection and task execution all existed inside one function, the modular architecture separates these responsibilities into distinct stages.

```
Speech

↓

Text

↓

Command Processor

↓

Classifier

↓

Dispatcher

↓

Scheduler
```

Every user request follows this pipeline.

No exceptions.

---

## Splitting Compound Commands

Humans rarely speak in perfectly isolated requests.

More commonly they say something like

> "Open YouTube and take a screenshot and tell me the time."

This is not one task.

It is three.

The command processor is responsible for recognizing this distinction.

The function

```
split_commands()
```

breaks a sentence into independent subcommands.

Current delimiters include

```
and

.
```

so the example above becomes

```
open youtube

take a screenshot

tell me the time
```

Each command is now completely independent.

They can be classified separately.

Scheduled separately.

Executed separately.

This decomposition is one of the reasons the scheduler remains simple.

The scheduler never has to understand English.

It receives already-separated work items.

---

## Independent Classification

Once commands are separated,

each one is classified independently.

For example

```
Open YouTube

↓

LOCAL
```

while

```
Write me a merge sort implementation

↓

CODE
```

Even though both originated from the same spoken sentence,

they become completely independent execution requests.

This greatly improves flexibility.

Future versions could even execute unrelated commands in parallel without changing the parsing logic.

---

## Local Priority Partitioning

One subtle optimization occurs before any task reaches the scheduler.

Suppose the user says

> "Write a Python program and open YouTube."

Technically,

the code request appeared first.

However,

opening a browser takes only milliseconds,

while code generation may require several seconds.

Executing them strictly in spoken order would therefore delay a nearly-instant action behind an expensive LLM call.

Instead,

the command processor partitions work.

Deterministic local actions execute first.

Everything else follows according to priority.

The result feels significantly more responsive while preserving correctness.

---

## Why Command Processing Exists

It would certainly be possible for the microphone to classify commands directly.

It would also be possible for the scheduler to perform classification.

Both designs increase coupling.

The command processor exists specifically to prevent that.

Each subsystem performs exactly one transformation.

```
Speech

↓

Text
```

```
Text

↓

Commands
```

```
Commands

↓

Intent
```

```
Intent

↓

Tasks
```

This pipeline is one of the largest architectural improvements introduced during the refactor.

---

# 7. Intent Classification

```
ai/classifier.py
```

Intent classification is where JARVIS decides *what* the user is asking.

Importantly,

this is **not** the same as deciding *how* to execute it.

Execution belongs to the dispatcher.

Classification belongs here.

Separating these responsibilities keeps the AI component entirely independent from execution logic.

---

## The Classification Waterfall

Classification deliberately proceeds from the cheapest possible solution toward the most expensive.

```
Deterministic Pattern

↓

Regex

↓

Keyword Detection

↓

LLM

↓

Agent
```

The overwhelming majority of requests never reach the language model.

This dramatically reduces latency.

---

## Stage 1 — Deterministic Parsing

The classifier first checks whether the request matches any known deterministic grammar.

Examples include

```
open

launch

pull up

start
```

These requests are passed directly into the browser subsystem.

No AI model is consulted.

The browser parser extracts

```
Site

↓

Browser
```

returning structured data rather than free text.

For example

```
Open GitHub in Brave
```

becomes

```
URL

↓

Browser

↓

Display Name
```

No inference.

No prompting.

No hallucination.

Pure deterministic parsing.

---

## Stage 2 — Local Commands

Several commands are recognized entirely through lightweight pattern matching.

Examples include

```
Screenshot

Time

Exit

Stop

Bye
```

Again,

none of these require an LLM.

The fastest solution is usually the most reliable solution.

---

## Stage 3 — AI Intent Classification

Only after every deterministic path has failed does JARVIS consult an AI model.

This decision is intentional.

Large language models are computationally expensive.

They are also inherently probabilistic.

Whenever deterministic code can answer a question,

it should.

The language model therefore becomes a fallback rather than the primary execution engine.

---

## Intent Categories

The classifier ultimately produces one of several intent categories.

```
LOCAL
```

Fast deterministic actions.

```
SYSTEM
```

Operating-system related requests.

```
SELF
```

Questions about JARVIS itself.

```
GENERAL
```

Conversation and knowledge.

```
CODE
```

Programming tasks.

```
AGENT
```

Multi-step reasoning requiring tools.

These categories are deliberately broad.

The dispatcher understands categories,

not English.

---

## Reverse Parsing

One interesting implementation detail appears inside the AI classifier.

Instead of reading the first classification character produced by the model,

the response is scanned backwards.

```
N

↓

GENERAL
```

Why?

Because smaller local models frequently produce responses such as

```
Sure!

The answer is N
```

Scanning forwards would incorrectly capture unrelated letters.

Scanning backwards almost always finds the actual classification token.

This tiny implementation detail dramatically improves reliability while remaining completely model-agnostic.

---

## Why Classification Lives Inside ai/

Notice that the classifier resides inside

```
ai/
```

rather than beside the scheduler.

This was a deliberate architectural decision.

Intent classification fundamentally belongs to the intelligence layer.

The scheduler should never know how AI prompting works.

Likewise,

the AI layer should never know how threads are managed.

Keeping these responsibilities separate makes both subsystems significantly easier to evolve independently.

---

# 8. Dispatcher

```
dispatcher.py
```

Classification produces intent.

Intent alone cannot execute anything.

Some component must translate

```
GENERAL
```

into

```
task_general()
```

That responsibility belongs entirely to the dispatcher.

The dispatcher is effectively a routing table.

Nothing more.

Given

```
Kind

↓

Payload
```

it returns

```
Function

↓

Arguments
```

This mapping exists in exactly one place.

Adding a new task therefore requires changing only one module rather than modifying multiple unrelated systems.

---

## Direct Execution

Not every request benefits from entering the priority queue.

Suppose the user says

> "Open YouTube."

Only one task exists.

Creating queue entries,

sorting priorities,

and dispatching through multiple layers adds unnecessary overhead.

The dispatcher therefore exposes

```
execute_direct()
```

for single-task execution.

Compound requests still use the scheduler queue.

Simple requests bypass it.

This optimization slightly reduces latency while keeping the scheduling model unchanged.

---

## Dispatch

Compound requests use

```
dispatch()
```

instead.

Each classified task is submitted to the scheduler with its associated priority.

The dispatcher itself performs no execution.

Its responsibility ends the moment work has been submitted.

This strict separation keeps routing logic independent from execution logic.

---

# 9. Task Handlers

```
tasks.py
```

Task handlers are where intent finally becomes action.

Unlike previous versions,

there is no giant chain of

```
if...

elif...

elif...
```

stretching hundreds of lines.

Each task exists as an independent function.

Examples include

```
task_open_url()

task_general()

task_code()

task_agent()

task_time()

task_screenshot()

task_exit()

task_system_operation()
```

Each function owns exactly one capability.

Nothing else.

---

## Why Separate Task Functions?

Consider the browser task.

Its job is remarkably small.

Receive

```
URL

Browser
```

Open the browser.

Speak confirmation.

Return.

It has no understanding of AI prompting.

No knowledge of memory.

No knowledge of scheduling.

Likewise,

the code-generation task knows absolutely nothing about browser automation.

Each function operates entirely within its own domain.

This dramatically reduces accidental coupling.

---

## AI Tasks

The general conversation task invokes

```
ollama_generate()
```

using

```
MODEL_GENERAL
```

The code-generation task instead invokes

```
MODEL_CODE
```

Nothing else changes.

Both tasks share the same client.

Only prompts and models differ.

This demonstrates one of the advantages of centralizing Ollama communication.

Changing the inference backend requires modifications in exactly one place.

---

## Agent Tasks

Agent execution deserves its own dedicated task.

Unlike conversation,

agent execution may involve several reasoning cycles,

multiple tool invocations,

and iterative observations.

Encapsulating this complexity inside

```
task_agent()
```

keeps the scheduler completely unaware of how agent reasoning operates.

To the scheduler,

an agent is simply another task.

That abstraction significantly simplifies the overall architecture.

# 10. Browser Resolution

```
browser.py
```

The browser subsystem exists because a dictionary is not intelligence.

Earlier versions of JARVIS relied on fixed mappings between phrases and actions.

```
"open youtube"

↓

https://youtube.com
```

This worked.

Until someone said

> Open YouTube in Brave.

The previous implementation had no concept of browsers.

It only knew complete phrases.

Adding support for Chrome required duplicating every supported website.

Adding Firefox required duplicating them again.

Adding Edge meant duplicating everything a third time.

The number of possible combinations grew exponentially.

The solution was not adding more dictionary entries.

The solution was decomposing the problem.

Instead of asking

> "Which sentence did the user say?"

the browser subsystem asks

> "Which site?"

and

> "Which browser?"

Those are fundamentally independent questions.

---

## Site Resolution

The first responsibility is determining what website the user wants.

Common websites are stored inside

```
SITE_SHORTCUTS
```

Examples include

```
YouTube

GitHub

Netflix

Gmail

ChatGPT

Google

Reddit
```

Exact matches resolve immediately.

If no exact match exists,

substring matching is attempted.

For example,

```
the youtube website
```

still resolves successfully because

```
youtube
```

appears inside the phrase.

If neither strategy succeeds,

the resolver checks whether the input already resembles a domain.

```
example.com
```

becomes

```
https://example.com
```

without consulting any lookup table.

Finally,

if everything else fails,

the request becomes a Google search.

Instead of producing an error,

JARVIS always attempts to produce something useful.

That graceful degradation is intentional.

The assistant should rarely respond with

"I don't know."

Opening a search result is usually more helpful.

---

## Browser Resolution

Browser names are handled completely independently.

Users rarely say exactly

```
chrome
```

They might instead say

```
Google Chrome

Chrome Browser

Brave Browser

Mozilla

Firefox
```

The browser resolver normalizes these variants into canonical browser identifiers.

```
Google Chrome

↓

chrome
```

```
Mozilla

↓

firefox
```

This normalization allows every downstream subsystem to work with a consistent representation.

---

## Cross-Platform Launchers

Launching a browser differs across operating systems.

Windows,

Linux,

and macOS all use different executables.

Rather than scattering platform-specific code throughout the project,

browser launch commands are centralized.

```
Platform

↓

Browser

↓

Launch Command
```

Every supported operating system has its own launcher table.

Adding support for another browser therefore requires editing only one structure.

---

## Parsing

The browser subsystem understands a surprisingly flexible grammar.

Examples include

```
Open GitHub

Launch Netflix

Pull up Reddit

Start YouTube
```

as well as

```
Open GitHub in Brave

Launch Netflix using Chrome

Start Reddit on Firefox
```

All of these map onto the same parser.

The parser extracts

```
Website

↓

Browser
```

and returns structured information.

No AI model participates.

No prompt is generated.

No inference occurs.

This deterministic parser is dramatically faster than routing browser commands through an LLM.

---

## Why Browser Logic Lives Alone

Opening websites appears simple.

It is not.

URL normalization,

browser aliases,

cross-platform launchers,

fallback behavior,

default browser support,

and parsing all represent separate concerns.

Grouping them inside one module isolates that complexity from the rest of the project.

Task handlers simply request

```
open_url_in_browser()
```

without caring how browser resolution actually works.

---

# 11. Persistent Memory

```
memory.py
```

Memory allows JARVIS to survive restarts.

Without it,

every conversation begins from zero.

The assistant immediately forgets user preferences,

ongoing projects,

and previous discussions.

Rather than storing every conversation forever,

JARVIS maintains two complementary representations.

```
Summary

+

Recent Turns
```

This hybrid approach combines long-term continuity with recent conversational accuracy.

---

## Recent Turns

The newest conversations are preserved exactly as spoken.

Nothing is summarized.

Nothing is rewritten.

Recent context remains verbatim.

This ensures the language model always sees the exact wording of the current discussion.

---

## Long-Term Summary

Older conversations are periodically compressed.

Rather than preserving every sentence,

the assistant asks the language model to produce a factual summary.

Only durable information is retained.

Examples include

- User preferences
- Ongoing projects
- Personal goals
- Important decisions

Greetings,

small talk,

and temporary conversation are intentionally discarded.

This prevents memory from growing without bound while preserving information that remains useful months later.

---

## Compression

Compression occurs automatically.

When the number of stored turns exceeds the configured threshold,

older conversations are summarized,

removed,

and replaced by an updated summary.

Memory therefore grows logarithmically rather than linearly.

This design eliminates the need for embeddings,

vector databases,

or semantic search while remaining remarkably effective for personal assistants.

---

## Thread Safety

Multiple worker threads may remember information simultaneously.

To prevent corruption,

all memory operations are protected by a lock.

Reading,

writing,

compressing,

and saving therefore behave atomically.

---

# 12. Ollama Client

```
ai/client.py
```

Every interaction with a language model passes through exactly one function.

```
ollama_generate()
```

Conversation.

Code generation.

Intent classification.

Memory summarization.

Agent reasoning.

Everything.

Centralizing inference provides two significant advantages.

First,

every request shares one implementation.

Second,

every error is handled consistently.

---

## Why One Client?

Imagine supporting another inference backend in the future.

Perhaps LM Studio.

Perhaps OpenAI.

Perhaps vLLM.

Without a central client,

every subsystem would require modification.

Instead,

changing inference requires updating one module.

Every caller continues using

```
ollama_generate()
```

exactly as before.

This abstraction significantly reduces future migration effort.

---

## Failure Handling

Several common failures are translated into meaningful runtime errors.

Examples include

- Ollama not running.
- Model missing.
- HTTP failures.
- Connection errors.

Rather than exposing low-level networking exceptions,

the client produces messages directly describing what the user should fix.

---

# 13. Agent Loop (ReAct)

```
ai/agent.py
```

Not every request can be answered directly.

Some require reasoning.

Others require searching.

Some require reading files before responding.

The agent loop exists specifically for these multi-step problems.

Unlike standard conversation,

agent execution alternates between thinking and acting.

```
Thought

↓

Action

↓

Observation

↓

Thought

↓

Action

↓

Observation
```

until eventually reaching

```
Final Answer
```

This architecture is commonly known as ReAct —

Reasoning plus Acting.

---

## Scratchpad

The agent maintains a continuously growing scratchpad.

Each reasoning step appends

```
Thought

Action

Observation
```

back into the prompt.

The next reasoning cycle therefore sees the complete history of previous reasoning.

This iterative process allows the model to adapt after every tool invocation.

---

## Safety

Infinite reasoning loops are prevented through

```
MAX_AGENT_STEPS
```

Once the limit is reached,

execution stops automatically.

This guarantees termination even if the model repeatedly fails to produce a final answer.

---

## Logging

Every reasoning step is written to

```
agent_log.txt
```

Unlike spoken responses,

the log preserves the entire reasoning process.

When debugging an agent,

this file is significantly more valuable than the final answer because it reveals exactly why a particular decision was made.

---

# 14. Parser

```
ai/parser.py
```

The agent communicates using text.

Python requires structure.

The parser bridges these two worlds.

Two regular expressions recognize the only legal outputs.

```
Action:

tool[input]
```

or

```
Final Answer:
```

Anything else is considered malformed.

Rather than allowing malformed reasoning to continue indefinitely,

execution terminates immediately.

This strict contract makes the interaction between deterministic code and probabilistic language models significantly more reliable.

---

# 15. Prompts

```
ai/prompts.py
```

Prompt engineering is treated as configuration rather than implementation.

System prompts are isolated from execution logic.

This separation offers several advantages.

Prompts can evolve independently.

Different models can receive different instructions.

Prompt experimentation requires modifying one file rather than searching the entire project.

Keeping prompts isolated also makes the architecture easier to understand.

Behavior belongs in prompts.

Execution belongs in Python.

---

# 16. Tool Registry

```
tools.py
```

Tools are the bridge between reasoning and action.

The language model itself cannot read files.

It cannot execute shell commands.

It cannot launch browsers.

Instead,

it requests that Python perform those actions.

Each tool exposes a common interface.

```
String

↓

Action

↓

String
```

This uniform contract allows the agent loop to treat every tool identically.

Whether reading a file,

executing a command,

or performing a web search,

the interaction pattern never changes.

The registry simply maps tool names to callable Python functions.

Adding a new capability therefore becomes a matter of registering one additional tool.

The reasoning engine requires no modification.

---

# 17. Sound Manager

```
sound.py
```

Notification sounds are intentionally treated as optional.

Failure to play a sound should never prevent task execution.

The sound manager therefore attempts playback only if the requested file exists.

Any playback error is silently ignored.

This philosophy reflects the importance of graceful degradation throughout the project.

A missing MP3 file should never crash a voice assistant.

---

# 18. Helpers

```
helpers.py
```

Some functionality belongs nowhere else.

Examples include

- Unicode sanitization
- Safe console printing
- Safe file writing
- Lazy module imports
- Common helper functions

Rather than duplicating these utilities throughout the project,

they are centralized inside a dedicated helper module.

One particularly important responsibility is protecting the application from Windows encoding failures.

Language models frequently generate Unicode punctuation.

Older Windows consoles frequently cannot display it correctly.

The helper layer sanitizes text before it reaches the console,

the filesystem,

or the speech engine.

This single module eliminates an entire class of Unicode-related crashes that affected earlier versions of JARVIS.</textarea>
</body>
</html>