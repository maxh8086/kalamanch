"""Stage 2: voice synthesis through the local Voicebox server.

Uses the OpenAI-compatible POST /v1/audio/speech route of Voicebox v0.5.0.
`voice` takes a profile name or id (GET /v1/models lists model ids).
VOICEBOX_MODEL must hold a model id from that list. Only local hosts are
expected; no cloud API is called.
"""

import os

DEFAULT_VOICEBOX_URL = "http://127.0.0.1:17493"
SPEECH_PATH = "/v1/audio/speech"


def synthesize(text, profile, out_path):
    """POST the text to Voicebox, write the WAV bytes to ``out_path``, return the path."""
    # Imported here so that importing this module does not require requests.
    import requests

    model = os.environ.get("VOICEBOX_MODEL")
    if not model:
        raise RuntimeError("VOICEBOX_MODEL is not set. Use a model id from GET /v1/models.")

    base = os.environ.get("VOICEBOX_URL", DEFAULT_VOICEBOX_URL).rstrip("/")
    url = f"{base}{SPEECH_PATH}"
    body = {"model": model, "input": text, "voice": profile, "response_format": "wav"}

    response = requests.post(url, json=body, timeout=600)
    if response.status_code != 200:
        raise RuntimeError(
            f"Voicebox request to {url} failed with HTTP {response.status_code}: "
            f"{response.text[:300]}"
        )
    with open(out_path, "wb") as fh:
        fh.write(response.content)
    return out_path
