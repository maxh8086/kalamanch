"""Remove Voicebox voice profiles 10 days after their video is accepted as final.

`record_final` stores the profiles used by an accepted edit in a local state
file. `cleanup` deletes only those recorded profiles, and only once the grace
period has passed. Profiles not in the state file are never touched.
"""

import json
import os
from datetime import datetime, timedelta, timezone

import requests

from kalamanch.voice import _base, resolve_profile_id

GRACE_DAYS = 10
STATE_ENV = "KALAMANCH_STATE"


def state_path():
    return os.environ.get(STATE_ENV) or os.path.join(os.path.expanduser("~"), ".kalamanch", "voices.json")


def load_state(path=None):
    path = path or state_path()
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_state(state, path=None):
    path = path or state_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def record_final(profile_names, now=None, path=None):
    """Mark the named profiles as used by an accepted final edit. Keeps the earliest accept time."""
    now = now or datetime.now(timezone.utc)
    state = load_state(path)
    base = _base()
    for name in profile_names:
        profile_id = resolve_profile_id(name, base)
        entry = state.setdefault(profile_id, {"name": name, "accepted_at": now.isoformat()})
        entry.pop("deleted_at", None)
    save_state(state, path)
    return sorted(profile_names)


def cleanup(now=None, grace_days=GRACE_DAYS, dry_run=False, path=None):
    """Delete recorded profiles whose grace period has passed. Return the names that are due."""
    now = now or datetime.now(timezone.utc)
    state = load_state(path)
    base = _base()
    due = []
    for profile_id, entry in state.items():
        if "deleted_at" in entry:
            continue
        accepted = datetime.fromisoformat(entry["accepted_at"])
        if accepted + timedelta(days=grace_days) > now:
            continue
        due.append(entry["name"])
        if dry_run:
            continue
        response = requests.delete(f"{base}/profiles/{profile_id}", timeout=60)
        if response.status_code not in (200, 204, 404):
            raise RuntimeError(
                f"Voicebox DELETE /profiles/{profile_id} failed with HTTP "
                f"{response.status_code}: {response.text[:300]}"
            )
        entry["deleted_at"] = now.isoformat()
    if not dry_run:
        save_state(state, path)
    return sorted(due)
