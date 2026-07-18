import threading

from helpers import (
    _lazy_import,
    safe_print,
    contains_phrase,
)

from sound import play_wake_sound

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
