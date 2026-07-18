import os

from config import CONFIG
from helpers import _lazy_import, safe_print


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