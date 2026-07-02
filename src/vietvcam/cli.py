from __future__ import annotations

import argparse
import logging
import sys
from contextlib import suppress
from pathlib import Path

import uvicorn

from .app import configure_logging, run_forever, run_once
from .api import create_app
from .config import load_settings
from .control_state import ControlStateStore
from .housekeeping import MediaHousekeeping
from .rtmp import RtmpIngestManager


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VietVCam service")
    parser.add_argument(
        "--once",
        action="store_true",
        help="run one cycle and exit",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="run HTTP upload API for iPhone clients",
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="run API and RTMP ingest together",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    settings = load_settings()
    configure_logging(settings.log_dir, settings.log_level)

    logging.getLogger("vietvcam").info("configuration loaded")
    if args.once:
        run_once(settings)
        return 0

    if args.api or args.hybrid:
        control_store = ControlStateStore(
            persist_path=Path("/var/lib/vietvcam/control_state.json")
        )
        app = create_app(settings, control_store=control_store)
        rtmp_manager = RtmpIngestManager(settings, control_store=control_store)
        keeper = MediaHousekeeping(settings)
        keeper.start()
        rtmp_manager.start()
        try:
            uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
        finally:
            with suppress(Exception):
                rtmp_manager.stop()
            with suppress(Exception):
                keeper.stop()
        return 0

    run_forever(settings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
