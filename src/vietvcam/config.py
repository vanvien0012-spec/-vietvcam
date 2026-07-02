from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8080
    log_level: str = "INFO"
    log_dir: Path = Path("/var/log/vietvcam")
    poll_seconds: int = 5
    upload_dir: Path = Path("/var/lib/vietvcam/uploads")
    max_upload_mb: int = 1024
    upload_token: str = ""
    rtmp_url: str = ""
    rtmp_record_dir: Path = Path("/var/lib/vietvcam/rtmp")
    rtmp_segment_seconds: int = 60
    media_retention_hours: int = 72
    media_max_total_gb: int = 20


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    parsed = int(value)
    if parsed < 1:
        raise ValueError(f"{name} must be >= 1")
    return parsed


def load_settings() -> Settings:
    return Settings(
        host=os.getenv("VIETVCAM_HOST", "127.0.0.1"),
        port=_int_env("VIETVCAM_PORT", 8080),
        log_level=os.getenv("VIETVCAM_LOG_LEVEL", "INFO").upper(),
        log_dir=Path(os.getenv("VIETVCAM_LOG_DIR", "/var/log/vietvcam")),
        poll_seconds=_int_env("VIETVCAM_POLL_SECONDS", 5),
        upload_dir=Path(
            os.getenv("VIETVCAM_UPLOAD_DIR", "/var/lib/vietvcam/uploads")
        ),
        max_upload_mb=_int_env("VIETVCAM_MAX_UPLOAD_MB", 1024),
        upload_token=os.getenv("VIETVCAM_UPLOAD_TOKEN", ""),
        rtmp_url=os.getenv("VIETVCAM_RTMP_URL", ""),
        rtmp_record_dir=Path(
            os.getenv("VIETVCAM_RTMP_RECORD_DIR", "/var/lib/vietvcam/rtmp")
        ),
        rtmp_segment_seconds=_int_env("VIETVCAM_RTMP_SEGMENT_SECONDS", 60),
        media_retention_hours=_int_env("VIETVCAM_MEDIA_RETENTION_HOURS", 72),
        media_max_total_gb=_int_env("VIETVCAM_MEDIA_MAX_TOTAL_GB", 20),
    )
