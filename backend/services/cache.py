"""Explanation cache. Owner: Jose. Story: NM-21.

One JSON file per customer in backend/cache/, committed to git so the demo never needs Wi-Fi:
    { "<customer>:<event>:<hash>": { "<option_id>": { "text": ..., "source": "llm" } } }
The hash covers everything the model is shown plus the prompt, so any change to the engine, the
persona data or the prompt makes the old entry a miss instead of serving stale numbers.
Written only by scripts/warm_cache.py; the API only reads.
"""
import hashlib
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


def cache_only() -> bool:
    """CACHE_ONLY=true: never call the LLM; serve the cache, or templates on a miss."""
    return os.environ.get("CACHE_ONLY", "").strip().lower() in ("1", "true", "yes")


def make_key(customer_id: str, life_event: dict | None, payload: dict, system_prompt: str) -> str:
    """f"{customer_id}:{event_type or 'none'}:{hash}", hashing the exact model input and prompt."""
    digest = hashlib.sha256(
        (json.dumps(payload, sort_keys=True) + "\n" + system_prompt).encode("utf-8")
    ).hexdigest()[:16]
    event_type = (life_event or {}).get("type") or "none"
    return f"{customer_id}:{event_type}:{digest}"


def _path(key: str) -> Path:
    return CACHE_DIR / f"{key.split(':', 1)[0]}.json"


def _read(path: Path) -> dict:
    """The whole file, or {} if it's missing or unreadable. Never raises."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as exc:
        logger.warning("Ignoring unreadable cache file %s: %r", path.name, exc)
        return {}


def get(key: str) -> dict | None:
    entry = _read(_path(key)).get(key)
    return entry if isinstance(entry, dict) else None


def put(key: str, explanations: dict) -> None:
    path = _path(key)
    data = _read(path)
    data[key] = explanations
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # sorted + indented so re-warming produces small, readable diffs
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
