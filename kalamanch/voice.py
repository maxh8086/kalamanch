"""Stage 2: voice synthesis through a local Voicebox REST server.

The endpoint path is unverified. Set VOICEBOX_TTS_PATH to match the
installed Voicebox server. Only local hosts are expected; no cloud API is called.
"""

import os

DEFAULT_VOICEBOX_URL = "http://127.0.0.1:17493"
DEFAULT_VOICEBOX_TTS_PATH = "/generate"


def synthesize(text, profile, out_path):
    """POST the text to Voicebox, write the response bytes to ``out_path``, return the path."""
    # Imported here so that importing this module does not require requests.
    import requests

    base = os.environ.get("VOICEBOX_URL", DEFAULT_VOICEBOX_URL).rstrip("/")
    path = os.environ.get("VOICEBOX_TTS_PATH", DEFAULT_VOICEBOX_TTS_PATH).lstrip("/")
    url = f"{base}/{path}"

    response = requests.post(url, json={"text": text, "profile": profile}, timeout=600)
    if response.status_code != 200:
        raise RuntimeError(
            f"Voicebox request to {url} failed with HTTP {response.status_code}: "
            f"{response.text[:300]}"
        )
    with open(out_path, "wb") as fh:
        fh.write(response.content)
    return out_path
