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