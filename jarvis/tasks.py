import os
import datetime
import requests
from ai.classifier import GENERAL_RULES, SYSTEM_RULES
from config import (
    CONFIG,
    MODEL_GENERAL,
    MODEL_CODE,
    OLLAMA_HOST,
)

from helpers import (
    _lazy_import,
    sanitize_text,
    safe_print,
    safe_write,
)



from ai.client import ollama_generate
from ai.agent import agent_loop

from memory import MEMORY

from browser import open_url_in_browser

from sound import (
    play_screenshot_sound,
    play_shutdown_sound,
    play_success_sound,
)

from scheduler import shutdown_event

from speech import speak

from util import speak_time_text

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
