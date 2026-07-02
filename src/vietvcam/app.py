from __future__ import annotations

import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import Settings


def configure_logging(log_dir: Path, level: str) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "vietvcam.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)


def run_once(settings: Settings) -> None:
    logger = logging.getLogger("vietvcam")
    logger.info(
        "health-check host=%s port=%s poll=%ss",
        settings.host,
        settings.port,
        settings.poll_seconds,
    )


def run_forever(settings: Settings) -> None:
    logger = logging.getLogger("vietvcam")
    logger.info("service started")
    try:
        while True:
            run_once(settings)
            time.sleep(settings.poll_seconds)
    except KeyboardInterrupt:
        logger.info("service stopped by keyboard interrupt")
