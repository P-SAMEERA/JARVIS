import re

# ============================================================
# Agent Output Parser
# ============================================================

ACTION_REGEX = re.compile(
    r"Action:\s*(\w+)\[(.*)\]",
    re.DOTALL
)

FINAL_REGEX = re.compile(
    r"Final Answer:\s*(.*)",
    re.DOTALL
)