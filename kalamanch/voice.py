"""Stage 2: voice synthesis through the local Voicebox server.

Uses the Voicebox v0.5.0 REST API on a local host:
  GET  /profiles             voice profile name -> id
  POST /generate             {profile_id, text} returns a generation record
  GET  /generate/{id}/status poll until the generation completes
  GET  /audio/{id}           WAV bytes of the finished generation
No cloud API is called.
"""

import os
import time

import requests

DEFAULT_VOICEBOX_URL = "http://127.0.0.1:17493"
POLL_SECONDS = 2
POLL_LIMIT_SECONDS = 600


def _base():
    return os.environ.get("VOICEBOX_URL", DEFAULT_VOICEBOX_URL).rstrip("/")


def _check(response, what):
    if response.status_code != 200:
        raise RuntimeError(
            f"Voicebox {what} failed with HTTP {response.status_code}: {response.text[:300]}"
        )
    return response


def unload_models():
    """Ask Voicebox to unload its TTS models so the GPU is free for the video stage.

    If Voicebox is not running, nothing is loaded, so return without error.
    """
    try:
        requests.post(f"{_base()}/models/unload", timeout=60)
    except requests.ConnectionError:
        return


def resolve_profile_id(profile, base):
    """Return the id of the profile whose name or id matches ``profile``."""
    profiles = _check(requests.get(f"{base}/profiles", timeout=30), "GET /profiles").json()
    for item in profiles:
        if profile in (item.get("name"), item.get("id")):
            return item["id"]
    raise RuntimeError(f"Voicebox has no voice profile named '{profile}'. Create it in Voicebox first.")


def synthesize(text, profile, out_path):
    """Generate speech for ``text`` with the named profile, write the WAV to ``out_path``."""
    base = _base()
    profile_id = resolve_profile_id(profile, base)

    generation = _check(
        requests.post(f"{base}/generate", json={"profile_id": profile_id, "text": text}, timeout=60),
        "POST /generate",
    ).json()
    generation_id = generation["id"]

    deadline = time.monotonic() + POLL_LIMIT_SECONDS
    status = generation.get("status")
    while status not in ("completed", "failed") and time.monotonic() < deadline:
        time.sleep(POLL_SECONDS)
        status = _check(
            requests.get(f"{base}/generate/{generation_id}/status", timeout=30),
            "status poll",
        ).json().get("status")
    if status != "completed":
        raise RuntimeError(f"Voicebox generation {generation_id} ended with status '{status}'.")

    audio = _check(requests.get(f"{base}/audio/{generation_id}", timeout=600), "GET /audio").content
    with open(out_path, "wb") as fh:
        fh.write(audio)
    return out_path
