from __future__ import annotations

import logging
import subprocess
import threading
import time
from pathlib import Path

from .config import Settings
from .control_state import ControlStateStore


class RtmpIngestManager:
    def __init__(
        self,
        settings: Settings,
        control_store: ControlStateStore | None = None,
    ) -> None:
        self.settings = settings
        self.control_store = control_store
        self._logger = logging.getLogger("vietvcam.rtmp")
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._process: subprocess.Popen[str] | None = None
        self._active_profile: str = ""

    def start(self) -> None:
        if not self.settings.rtmp_url:
            self._logger.info("RTMP disabled: VIETVCAM_RTMP_URL is empty")
            return
        self.settings.rtmp_record_dir.mkdir(parents=True, exist_ok=True)
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._logger.info("RTMP ingest manager started")

    def stop(self) -> None:
        self._stop_event.set()
        self._terminate_process()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self._logger.info("RTMP ingest manager stopped")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            stream_url = self._current_stream_url()
            if not stream_url:
                time.sleep(1)
                continue
            profile = self._current_filter_profile()
            if self._process and profile != self._active_profile:
                self._logger.info("control filter changed, restarting ffmpeg")
                self._terminate_process()

            if self._process and self._process.poll() is None:
                time.sleep(1)
                continue

            output_pattern = str(
                Path(self.settings.rtmp_record_dir)
                / "rtmp_%Y%m%d_%H%M%S.mp4"
            )
            video_filter = self._build_video_filter()
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "warning",
                "-i",
                stream_url,
                "-vf",
                video_filter,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-f",
                "segment",
                "-segment_time",
                str(self.settings.rtmp_segment_seconds),
                "-reset_timestamps",
                "1",
                "-segment_format",
                "mp4",
                output_pattern,
            ]
            self._active_profile = profile
            self._logger.info("starting ffmpeg RTMP ingest with filters")
            self._process = subprocess.Popen(cmd, text=True)
            time.sleep(1)
            if self._process.poll() is not None:
                exit_code = self._process.returncode
                self._process = None
                if self._stop_event.is_set():
                    return
                self._logger.warning(
                    "ffmpeg stopped with code %s, retrying in 3s", exit_code
                )
                time.sleep(3)

    def _terminate_process(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None

    def _current_stream_url(self) -> str:
        if not self.control_store:
            return self.settings.rtmp_url
        snap = self.control_store.snapshot()
        override = str(snap.get("stream_url", "")).strip()
        connected = bool(snap.get("connected", False))
        if connected and override:
            return override
        return self.settings.rtmp_url

    def _current_filter_profile(self) -> str:
        if not self.control_store:
            return "default"
        snap = self.control_store.snapshot()
        return (
            f"b={int(snap.get('brightness', 0))};"
            f"c={int(snap.get('contrast', 0))};"
            f"s={int(snap.get('sharpness', 0))};"
            f"z={float(snap.get('zoom', 1.0)):.2f};"
            f"x={int(snap.get('x', 0))};"
            f"y={int(snap.get('y', 0))}"
        )

    def _build_video_filter(self) -> str:
        if not self.control_store:
            return "null"
        snap = self.control_store.snapshot()
        brightness = max(-100, min(100, int(snap.get("brightness", 0))))
        contrast = max(-100, min(100, int(snap.get("contrast", 0))))
        sharpness = max(0, min(100, int(snap.get("sharpness", 0))))
        zoom = max(0.2, min(4.0, float(snap.get("zoom", 1.0))))

        eq_brightness = brightness / 100.0
        eq_contrast = 1.0 + (contrast / 100.0)
        unsharp = sharpness / 12.0
        crop_factor = min(1.0, 1.0 / zoom)
        crop_w = f"iw*{crop_factor:.6f}"
        crop_h = f"ih*{crop_factor:.6f}"

        # Keep x/y integration lightweight and bounded in expressions.
        x_shift = int(snap.get("x", 0))
        y_shift = int(snap.get("y", 0))
        x_expr = f"(iw-{crop_w})/2+{x_shift}"
        y_expr = f"(ih-{crop_h})/2+{y_shift}"
        return (
            f"eq=brightness={eq_brightness:.3f}:contrast={eq_contrast:.3f},"
            f"unsharp=5:5:{unsharp:.2f}:5:5:{unsharp:.2f},"
            f"crop={crop_w}:{crop_h}:{x_expr}:{y_expr},"
            f"scale=trunc(iw/{crop_factor:.6f}):trunc(ih/{crop_factor:.6f})"
        )
