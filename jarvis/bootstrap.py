import datetime
import sys

import requests

from config import (
    OLLAMA_HOST,
    MODEL_GENERAL,
    MODEL_CODE,
)

from helpers import safe_print

from sound import (
    play_startup_sound,
)

from speech import (
    speak,
    get_speech_worker,
)

from scheduler import PriorityScheduler

from microphone import MicListener


# ============================================================
# Startup Banner
# ============================================================

def startup_banner():

    safe_print("=" * 60)
    safe_print("JARVIS")
    safe_print("=" * 60)


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
# Initialize
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
            raise RuntimeError(f"{MODEL_GENERAL} not found.")

        if MODEL_CODE not in model_names:
            raise RuntimeError(f"{MODEL_CODE} not found.")

        safe_print("[init] Ollama Connected")

    except Exception as e:

        safe_print(f"[init] {e}")

        speak("Unable to connect to Ollama.")

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

    wish()

    safe_print()
    safe_print("=" * 60)
    safe_print("JARVIS ONLINE")
    safe_print("=" * 60)

    return scheduler, microphone