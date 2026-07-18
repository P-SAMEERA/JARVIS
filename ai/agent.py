import datetime

from config import (
    AGENT_MAX_STEPS,
    CONFIG,
)

from helpers import safe_write

from tools import TOOL_REGISTRY

from ai.client import ollama_generate
from ai.prompts import AGENT_SYSTEM_PROMPT
from ai.parser import ACTION_REGEX, FINAL_REGEX
from config import MODEL_GENERAL



def log_agent_trace(

    goal: str,

    trace: str

):

    safe_write(

        CONFIG["AGENT_LOG"],

        f"""
GOAL

{goal}

TRACE

{trace}

TIME

{datetime.datetime.now()}

{'=' * 80}

"""

    )


def agent_loop(

    goal: str,

    memory_context: str = ""

):

    scratchpad = ""

    for _ in range(AGENT_MAX_STEPS):

        prompt = ""

        if memory_context:

            prompt += (

                memory_context

                +

                "\n\n"

            )

        prompt += f"Goal : {goal}\n\n"

        prompt += scratchpad

        try:

            response = ollama_generate(

                system_prompt=AGENT_SYSTEM_PROMPT,

                user_prompt=prompt,

                model=MODEL_GENERAL,

                max_tokens=400,

                temperature=0.3

            )

        except Exception as e:

            return f"Agent Error : {e}"

        final = FINAL_REGEX.search(response)

        if final:

            scratchpad += "\n" + response

            log_agent_trace(

                goal,

                scratchpad

            )

            return final.group(1).strip()

        action = ACTION_REGEX.search(response)

        if not action:

            log_agent_trace(

                goal,

                scratchpad

                +

                response

            )

            return response.strip()

        tool_name = action.group(1).strip()

        tool_input = action.group(2).strip()

        tool = TOOL_REGISTRY.get(tool_name)

        if tool:

            observation = tool(tool_input)

        else:

            observation = (

                f"Unknown Tool : {tool_name}"

            )

        scratchpad += f"""

{response}

Observation:

{observation}

"""

    log_agent_trace(

        goal,

        scratchpad

    )

    return (
        "Maximum reasoning steps reached.\n\n"

        +

        scratchpad[-1000:]

    )
