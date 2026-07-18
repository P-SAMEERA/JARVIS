import threading
import queue

from helpers import (
    _lazy_import,
    safe_print,
    sanitize_text,
)

from config import CONFIG

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
