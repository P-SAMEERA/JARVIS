import requests

from config import OLLAMA_HOST
from helpers import safe_print


# ============================================================
# Ollama Client
# ============================================================

def ollama_generate(
    system_prompt: str,
    user_prompt: str,
    model: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:

        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=180,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            f"Couldn't connect to Ollama at {OLLAMA_HOST}. "
            f"Is 'ollama serve' running?"
        )

    except requests.exceptions.HTTPError as e:

        raise RuntimeError(
            f"Ollama rejected the request ({e}). "
            f"Model '{model}' may not exist."
        )

    except Exception as e:

        safe_print(f"[ollama] {e}")
        raise

    data = response.json()

    return (
        data.get("message", {})
            .get("content", "")
            .strip()
    )