import os
import json
import datetime
import threading

from config import (
    MEMORY_FILE,
    MEMORY_MAX_RAW_TURNS,
    MODEL_GENERAL,
)

from helpers import safe_print
from ai.client import ollama_generate


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