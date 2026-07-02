from vietvcam.config import load_settings


def test_default_config(monkeypatch):
    monkeypatch.delenv("VIETVCAM_PORT", raising=False)
    monkeypatch.delenv("VIETVCAM_POLL_SECONDS", raising=False)
    settings = load_settings()
    assert settings.port == 8080
    assert settings.poll_seconds == 5


def test_env_override(monkeypatch):
    monkeypatch.setenv("VIETVCAM_PORT", "9090")
    monkeypatch.setenv("VIETVCAM_POLL_SECONDS", "9")
    monkeypatch.setenv("VIETVCAM_MAX_UPLOAD_MB", "256")
    monkeypatch.setenv("VIETVCAM_UPLOAD_TOKEN", "secret")
    monkeypatch.setenv("VIETVCAM_RTMP_URL", "rtmp://example/live/stream")
    monkeypatch.setenv("VIETVCAM_RTMP_SEGMENT_SECONDS", "30")
    monkeypatch.setenv("VIETVCAM_MEDIA_RETENTION_HOURS", "24")
    monkeypatch.setenv("VIETVCAM_MEDIA_MAX_TOTAL_GB", "5")
    settings = load_settings()
    assert settings.port == 9090
    assert settings.poll_seconds == 9
    assert settings.max_upload_mb == 256
    assert settings.upload_token == "secret"
    assert settings.rtmp_url == "rtmp://example/live/stream"
    assert settings.rtmp_segment_seconds == 30
    assert settings.media_retention_hours == 24
    assert settings.media_max_total_gb == 5
