import threading
import time
from typing import Any, Dict, Iterable, List, Tuple

from config import settings
from db import fetch_all


_LOCK = threading.RLock()
_ROWS: Dict[str, Dict[str, Any]] = {}


def _ttl() -> int:
    return max(1, int(getattr(settings, "CACHE_TTL_SECONDS", 300) or 300))


def get_rows(key: str, sql: str, force_refresh: bool = False, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    now = time.time()
    with _LOCK:
        entry = _ROWS.get(key)
        if (
            not force_refresh
            and entry
            and (now - float(entry.get("loaded_at") or 0)) <= _ttl()
        ):
            return entry.get("rows") or []

    rows = fetch_all(sql, params)
    with _LOCK:
        _ROWS[key] = {"loaded_at": time.time(), "rows": rows}
    return rows


def clear() -> None:
    with _LOCK:
        _ROWS.clear()


def warm(definitions: Iterable[Tuple[str, str]]) -> None:
    for key, sql in definitions:
        try:
            get_rows(key, sql, force_refresh=False)
        except Exception:
            # Individual services already handle missing views gracefully.
            pass
