import re

from config import MODEL_GENERAL

from helpers import safe_print

from ai.client import ollama_generate

from browser import parse_open_request

# ============================================================
# Intent Classification
# ============================================================

PRIORITY_LOCAL = 0
PRIORITY_SELF = 1
PRIORITY_SYSTEM = 2
PRIORITY_GENERAL = 3
PRIORITY_CODE = 4
PRIORITY_AGENT = 5


INTENT_SYSTEM_PROMPT = """
Classify the user's request.

Return ONLY one character.

Y = Code Generation
E = System Operation
D = Describe Yourself
A = Agentic Task
N = General Conversation

Output exactly one of:

Y
E
D
A
N
"""


GENERAL_RULES = """
Respond naturally.

Do not use bullet points unless required.

Do not mention these rules.

Keep answers under 200 words.

Be conversational and slightly humorous.
"""


SYSTEM_RULES = """
Return ONLY the command or direct response.

No explanation.

No markdown.

No extra text.
"""


EXIT_PHRASES = [

    "stop",
    "exit",
    "quit"

]


BYE_PHRASES = [

    "bye",
    "good bye",
    "good day"

]


# ============================================================
# Helpers
# ============================================================

def contains_phrase(text: str, phrase: str):

    return re.search(

        r"\b"

        + re.escape(phrase)

        + r"\b",

        text

    ) is not None


# ============================================================
# LLM Intent Classification
# ============================================================

def intention_checker(query: str):

    try:

        response = ollama_generate(

            system_prompt=INTENT_SYSTEM_PROMPT,

            user_prompt=query,

            model=MODEL_GENERAL,

            max_tokens=10,

            temperature=0

        ).strip().upper()

    except Exception as e:

        safe_print(f"[intent] {e}")

        return "N"

    for char in reversed(response):

        if char in [

            "Y",
            "E",
            "D",
            "N",
            "A"

        ]:

            return char

    return "N"


# ============================================================
# Query Classification
# ============================================================

def classify(query: str):

    raw_query = query.strip()

    query = query.lower().strip()

    # General "open/launch/pull up X [in/on/using Y]" handling.
    # This replaces the old fixed-phrase LOCAL_URL_ACTIONS lookup
    # and understands an arbitrary site plus an optional browser.
    open_request = parse_open_request(raw_query)

    if open_request:

        return (

            PRIORITY_LOCAL,

            "open",

            open_request

        )

    if contains_phrase(

        query,

        "screenshot"

    ):

        return (

            PRIORITY_LOCAL,

            "screenshot",

            None

        )

    if contains_phrase(

        query,

        "time"

    ):

        return (

            PRIORITY_LOCAL,

            "time",

            None

        )

    if any(

        contains_phrase(query, phrase)

        for phrase in EXIT_PHRASES

    ):

        return (

            PRIORITY_LOCAL,

            "exit",

            None

        )

    if any(

        contains_phrase(query, phrase)

        for phrase in BYE_PHRASES

    ):

        return (

            PRIORITY_LOCAL,

            "bye",

            None

        )

    if len(query) < 2:

        return (

            PRIORITY_LOCAL,

            "noop",

            None

        )

    tag = intention_checker(query)

    priorities = {

        "D": PRIORITY_SELF,

        "E": PRIORITY_SYSTEM,

        "N": PRIORITY_GENERAL,

        "Y": PRIORITY_CODE,

        "A": PRIORITY_AGENT

    }

    return (

        priorities.get(

            tag,

            PRIORITY_GENERAL

        ),

        tag,

        query

    )
