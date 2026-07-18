import os
import re
import subprocess

import requests
from helpers import safe_print

from config import TOOL_TIMEOUT_SECONDS
from browser import (
    resolve_browser_alias,
    resolve_site_url,
    open_url_in_browser,
)


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

