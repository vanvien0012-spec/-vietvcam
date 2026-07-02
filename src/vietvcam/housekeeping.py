from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from .config import Settings


class MediaHousekeeping:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._logger = logging.getLogger("vietvcam.housekeeping")
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._logger.info("media housekeeping started")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self._logger.info("media housekeeping stopped")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._cleanup()
            except Exception as exc:  # defensive loop
                self._logger.warning("cleanup error: %s", exc)
            self._stop_event.wait(timeout=300)

    def _cleanup(self) -> None:
        now = time.time()
        ttl = self.settings.media_retention_hours * 3600
        targets = [self.settings.upload_dir, self.settings.rtmp_record_dir]
        files: list[Path] = []

        for base in targets:
            if not base.exists():
                continue
            files.extend([p for p in base.glob("*") if p.is_file()])

        removed_by_age = 0
        for f in files:
            age = now - f.stat().st_mtime
            if age > ttl:
                f.unlink(missing_ok=True)
                removed_by_age += 1

        files = []
        for base in targets:
            if not base.exists():
                continue
            files.extend([p for p in base.glob("*") if p.is_file()])

        max_bytes = self.settings.media_max_total_gb * 1024 * 1024 * 1024
        files_sorted = sorted(files, key=lambda p: p.stat().st_mtime)
        total = sum(p.stat().st_size for p in files_sorted)
        removed_by_size = 0
        for f in files_sorted:
            if total <= max_bytes:
                break
            size = f.stat().st_size
            f.unlink(missing_ok=True)
            total -= size
            removed_by_size += 1

        if removed_by_age or removed_by_size:
            self._logger.info(
                "cleanup removed age=%s size=%s remaining_bytes=%s",
                removed_by_age,
                removed_by_size,
                total,
            )
