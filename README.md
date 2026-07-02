# VietVCam

VietVCam is a production-style Python service template ready to package as a Debian `.deb`.

## Features

- Typed configuration loaded from environment variables.
- Rotating file logs plus console logs.
- Clean start/stop flow for systemd.
- Hybrid mode: RTMP ingest + direct iPhone upload in one service.
- Debian packaging scripts for repeatable builds.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip build
pip install -e .
vietvcam --once
```

## Runtime environment variables

- `VIETVCAM_HOST` (default: `127.0.0.1`)
- `VIETVCAM_PORT` (default: `8080`)
- `VIETVCAM_LOG_LEVEL` (default: `INFO`)
- `VIETVCAM_LOG_DIR` (default: `/var/log/vietvcam`)
- `VIETVCAM_POLL_SECONDS` (default: `5`)
- `VIETVCAM_UPLOAD_DIR` (default: `/var/lib/vietvcam/uploads`)
- `VIETVCAM_MAX_UPLOAD_MB` (default: `1024`)
- `VIETVCAM_UPLOAD_TOKEN` (default: empty, no token check)
- `VIETVCAM_RTMP_URL` (default: empty, disabled)
- `VIETVCAM_RTMP_RECORD_DIR` (default: `/var/lib/vietvcam/rtmp`)
- `VIETVCAM_RTMP_SEGMENT_SECONDS` (default: `60`)
- `VIETVCAM_MEDIA_RETENTION_HOURS` (default: `72`)
- `VIETVCAM_MEDIA_MAX_TOTAL_GB` (default: `20`)

## iPhone upload mode

Start API mode:

```bash
vietvcam --api
```

Upload test (from another machine or iPhone shortcut):

```bash
curl -X POST "http://SERVER_IP:8080/upload" \
  -H "x-upload-token: YOUR_TOKEN" \
  -F "file=@sample.mp4"
```

Open iPhone control panel:

```bash
https://YOUR_DOMAIN/control
```

Control API:

- `GET /control/state` returns `{x, y, zoom}`
- `GET /control/audit` returns recent operator actions (last 200)
- `GET /control/audit-ui` opens action history page on mobile
- `POST /control/audit/clear` clears action history
- `POST /control/move` with actions for:
  - control: `left|right|up|down|zoom_in|zoom_out|reset|disable_vcam|hide|close`
  - source: `source_1..source_6|play|pause|connect|disconnect`
  - light: `set_value` (`brightness|contrast|sharpness|light_intensity`), `light_reset`, `apply_preset`
- `GET /control/presets` lists available presets (`low_light`, `natural`, `sharp`)
- `POST /control/preset/save` saves current slider values as custom preset
- `POST /control/preset/rename` renames custom preset
- `POST /control/preset/delete` deletes custom preset by name
- `GET /control/preset/export` exports custom presets JSON
- `POST /control/preset/import` imports custom presets JSON

Operator safety mode:

- Control panel is a separate web UI and does not inject/overlay into target apps.
- Use only for authorized testing/demo workflows.

## Hybrid mode (RTMP + iPhone direct upload)

Run with RTMP ingest enabled while still accepting iPhone uploads:

```bash
export VIETVCAM_RTMP_URL="rtmp://YOUR_SERVER/live/stream_key"
export VIETVCAM_UPLOAD_TOKEN="YOUR_TOKEN"
vietvcam --hybrid
```

- RTMP recordings are saved to `/var/lib/vietvcam/rtmp`.
- iPhone uploaded media is saved to `/var/lib/vietvcam/uploads`.
- Service runs as non-root `vietvcam` user with systemd hardening.
- In hybrid mode, `brightness/contrast/sharpness/zoom/x/y` from `/control` are applied to the RTMP recording pipeline via ffmpeg filters.

### Real-time filter behavior

- Update sliders/buttons on `/control`, the RTMP ffmpeg process auto-restarts with the new filter profile.
- `Source -> Connect` stream URL (if set) overrides `VIETVCAM_RTMP_URL` while connected.
- Preset chosen on iPhone is persisted to `/var/lib/vietvcam/control_state.json` and restored after service restart.
- Custom presets are persisted to `/var/lib/vietvcam/custom_presets.json`.

## Production notes

- Main runtime settings are in `/etc/default/vietvcam` after install.
- Use Nginx/Caddy in front for HTTPS, proxy to `127.0.0.1:8080`.
- Rotate upload token regularly for better security.
- Ready-to-use Nginx config: `deploy/nginx/vietvcam.conf`.
- HTTPS deployment steps: `deploy/nginx/README.md`.

## Build a Debian package

```bash
chmod +x scripts/build_deb.sh
./scripts/build_deb.sh
```

The script outputs `dist/vietvcam_1.0.0_all.deb`.

## Build a Sileo (rootless) package

### Option A: Launcher only (legacy)

```bash
chmod +x scripts/build_sileo_deb.sh
./scripts/build_sileo_deb.sh
```

Output: `dist/vietvcam-control_1.0.0_iphoneos-arm64.deb` (opens web control URL)

### Option B: Standalone iOS app (recommended for 1,2,4)

Build on Mac/Linux with Theos:

```bash
export THEOS=~/theos
chmod +x scripts/build_ios_app.sh
./scripts/build_ios_app.sh
```

See `ios/README_BUILD.md` for full details.

### Build without Mac (GitHub Actions)

See `BUILD_CI.md` — push to GitHub and download `.deb` from Actions artifacts.

Output: `dist/com.vanvi.vietvcam_*_iphoneos-arm64.deb`

Features:
- App icon on iPhone (no Safari)
- Source tab for RTMP/HLS stream URL
- Control + Light tabs for zoom and image tuning

## Build a Sileo repository

Build package first:

```bash
./scripts/build_sileo_deb.sh
```

Then generate local repo metadata:

```bash
chmod +x scripts/build_sileo_repo.sh
./scripts/build_sileo_repo.sh
```

Serve repo on your PC:

```bash
cd repo-sileo
python3 -m http.server 8888
```

Add source in Sileo:

- `http://<YOUR_PC_IP>:8888`
