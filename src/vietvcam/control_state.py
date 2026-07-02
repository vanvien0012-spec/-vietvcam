from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Any


class ControlStateStore:
    def __init__(self, persist_path: Path | None = None) -> None:
        self._lock = Lock()
        self._persist_path = persist_path
        self._state: dict[str, Any] = {
            "x": 0,
            "y": 0,
            "zoom": 1.0,
            "source": 1,
            "paused": False,
            "stream_url": "",
            "connected": False,
            "brightness": 0,
            "contrast": 0,
            "sharpness": 0,
            "light_intensity": 50,
            "preset": "natural",
        }
        self._load_if_exists()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)

    def update(self, updates: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._state.update(updates)
            self._persist()
            return deepcopy(self._state)

    def mutate(self, fn: Any) -> dict[str, Any]:
        with self._lock:
            fn(self._state)
            self._persist()
            return deepcopy(self._state)

    def _load_if_exists(self) -> None:
        if not self._persist_path:
            return
        if not self._persist_path.exists():
            return
        try:
            raw = json.loads(self._persist_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self._state.update(raw)
        except Exception:
            # Ignore invalid saved state and keep defaults.
            return

    def _persist(self) -> None:
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._persist_path.write_text(
            json.dumps(self._state, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
