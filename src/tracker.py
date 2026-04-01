"""
Tracks which post IDs have already been posted.
Uses a simple JSON file. On Railway, mount a persistent volume at /data
or use a free Redis/PostgreSQL add-on for true persistence across deploys.
"""
import json
import os
import logging

log = logging.getLogger(__name__)

TRACKER_FILE = os.environ.get("TRACKER_PATH", "/data/posted.json")


def _load() -> set:
    try:
        with open(TRACKER_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def _save(ids: set):
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    # Keep only last 5000 IDs to prevent file from growing forever
    trimmed = list(ids)[-5000:]
    with open(TRACKER_FILE, "w") as f:
        json.dump(trimmed, f)


def was_posted(post_id: str) -> bool:
    return post_id in _load()


def mark_posted(post_id: str):
    ids = _load()
    ids.add(post_id)
    _save(ids)
    log.debug(f"Marked as posted: {post_id}")
