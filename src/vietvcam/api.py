from __future__ import annotations

import json
import time
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from .config import Settings
from .control_state import ControlStateStore

PRESETS: dict[str, dict[str, int | str]] = {
    "low_light": {
        "brightness": 28,
        "contrast": 18,
        "sharpness": 26,
        "light_intensity": 72,
        "preset": "low_light",
    },
    "natural": {
        "brightness": 0,
        "contrast": 0,
        "sharpness": 14,
        "light_intensity": 50,
        "preset": "natural",
    },
    "sharp": {
        "brightness": -4,
        "contrast": 8,
        "sharpness": 48,
        "light_intensity": 54,
        "preset": "sharp",
    },
}


def _safe_suffix(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if not suffix or len(suffix) > 10:
        return ".bin"
    return suffix


def _sanitize_preset_name(raw_name: str) -> str:
    clean = "".join(c for c in raw_name.strip().lower() if c.isalnum() or c in {"_", "-"})
    return clean[:32]


def create_app(
    settings: Settings,
    control_store: ControlStateStore | None = None,
) -> FastAPI:
    app = FastAPI(title="VietVCam Upload API", version="1.0.0")
    logger = logging.getLogger("vietvcam.api")
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    audit_log: list[dict[str, str | int | float | bool]] = []
    store = control_store or ControlStateStore()
    custom_presets_path = Path("/var/lib/vietvcam/custom_presets.json")
    custom_presets: dict[str, dict[str, int | str]] = {}

    def _load_custom_presets() -> None:
        nonlocal custom_presets
        if not custom_presets_path.exists():
            custom_presets = {}
            return
        try:
            data = json.loads(custom_presets_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cleaned: dict[str, dict[str, int | str]] = {}
                for name, values in data.items():
                    if not isinstance(name, str) or not isinstance(values, dict):
                        continue
                    cleaned[name] = {
                        "brightness": int(values.get("brightness", 0)),
                        "contrast": int(values.get("contrast", 0)),
                        "sharpness": int(values.get("sharpness", 0)),
                        "light_intensity": int(values.get("light_intensity", 50)),
                        "preset": str(values.get("preset", name)),
                    }
                custom_presets = cleaned
        except Exception:
            custom_presets = {}

    def _save_custom_presets() -> None:
        custom_presets_path.parent.mkdir(parents=True, exist_ok=True)
        custom_presets_path.write_text(
            json.dumps(custom_presets, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    _load_custom_presets()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    def _append_audit(action: str, detail: str = "") -> None:
        snap = store.snapshot()
        entry = {
            "ts": int(time.time()),
            "action": action,
            "detail": detail[:200],
            "x": snap["x"],
            "y": snap["y"],
            "zoom": snap["zoom"],
            "source": snap["source"],
            "connected": snap["connected"],
        }
        audit_log.append(entry)
        if len(audit_log) > 200:
            del audit_log[: len(audit_log) - 200]

    @app.get("/control", response_class=HTMLResponse)
    async def control_page() -> str:
        return """<!doctype html>
<html lang="en">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta charset="utf-8">
  <title>VietVCam Control</title>
  <style>
    body { font-family: -apple-system, Arial, sans-serif; margin: 0; background: #071024; color: #eef2ff; }
    .wrap { max-width: 420px; margin: 0 auto; padding: 14px; }
    .title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .sub { font-size: 12px; opacity: .82; margin-bottom: 10px; }
    .status { font-size: 13px; line-height: 1.6; margin-bottom: 10px; }
    .panel { background: linear-gradient(180deg,#7b7f8c,#676b78); border-radius: 14px; padding: 10px; border: 2px solid #d1b24b; box-shadow: 0 10px 24px rgba(0,0,0,.35); }
    .tabs { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-bottom:8px; }
    .tab { border:0; border-radius:8px; padding:7px 4px; font-size:12px; font-weight:700; background:#d1d5db; color:#111827; }
    .tab.active { background:#2282ff; color:#fff; }
    .pane { display:none; }
    .pane.active { display:block; }
    .row3 { display:grid; grid-template-columns: repeat(3, 1fr); gap:7px; margin-bottom:7px; }
    .row2 { display:grid; grid-template-columns: repeat(2, 1fr); gap:7px; margin-bottom:7px; }
    button { border:0; border-radius:9px; padding:10px 6px; font-size:15px; font-weight:700; color:#fff; background:#6b7280; }
    button:active { transform: scale(0.97); filter: brightness(1.08); }
    .k-blue { background:#2282ff; }
    .k-orange { background:#ff9800; }
    .k-red { background:#ff3b30; }
    .k-green { background:#34c759; }
    .k-gray { background:#a1a1aa; color:#111827; }
    .k-purple { background:#4f46e5; }
    .k-cyan { background:#28b7d8; }
    .input { width:100%; box-sizing:border-box; border:0; border-radius:8px; padding:10px; font-size:13px; color:#e5e7eb; background:#1f2a44; margin-bottom:7px; }
    .label { font-size:12px; margin:6px 2px; color:#f3f4f6; }
    input[type=range] { width:100%; }
    .tiny { font-size:12px; opacity:0.9; }
    .audit-link { display:block; margin-top:8px; text-align:center; color:#93c5fd; text-decoration:none; font-size:12px; }
    .preset-row { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; margin-bottom:7px; }
    .preset-row button { font-size:12px; }
    .preset-tools { display:grid; grid-template-columns: 1fr 1fr; gap:7px; margin-bottom:7px; }
    .preset-list { display:grid; grid-template-columns:repeat(2,1fr); gap:7px; margin-bottom:7px; }
    .preset-list-actions { display:grid; grid-template-columns:repeat(2,1fr); gap:7px; margin-bottom:7px; }
    .textarea { width:100%; box-sizing:border-box; border:0; border-radius:8px; padding:10px; font-size:12px; color:#e5e7eb; background:#1f2a44; margin-bottom:7px; min-height:100px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="title">VietVCam iPhone Control</div>
    <div class="sub">Control + Source RTMP + Light (brightness/sharpness). Transparent operator mode only.</div>
    <div id="state" class="status">x: 0 | y: 0 | zoom: 1.00x | source: 1 | preset: natural</div>
    <div class="panel">
      <div class="tabs">
        <button id="tab-control" class="tab active" onclick="openTab('control')">Control</button>
        <button id="tab-source" class="tab" onclick="openTab('source')">Source</button>
        <button id="tab-light" class="tab" onclick="openTab('light')">Light</button>
      </div>

      <div id="pane-control" class="pane active">
        <div class="row3">
          <button class="k-cyan" onclick="send('left')">←</button>
          <button class="k-gray" onclick="send('reset')">⟲</button>
          <button class="k-cyan" onclick="send('right')">→</button>
        </div>
        <div class="row3">
          <button class="k-red" onclick="send('zoom_out')">-</button>
          <button class="k-green" onclick="send('down')">↓</button>
          <button class="k-red" onclick="send('zoom_in')">+</button>
        </div>
        <div class="row2">
          <button class="k-red" onclick="send('disable_vcam')">Disable VCam</button>
          <button class="k-purple" onclick="send('pause')">Pause</button>
        </div>
        <div class="row2">
          <button class="k-gray" onclick="send('hide')">Hide</button>
          <button class="k-red" onclick="send('close')">Close</button>
        </div>
      </div>

      <div id="pane-source" class="pane">
        <div class="row3">
          <button class="k-gray" onclick="send('source_4')">4</button>
          <button class="k-gray" onclick="send('source_5')">5</button>
          <button class="k-gray" onclick="send('source_6')">6</button>
        </div>
        <div class="row2">
          <button class="k-orange" onclick="send('play')">▶ Play</button>
          <button class="k-purple" onclick="send('pause')">Pause</button>
        </div>
        <div class="label">Live Stream (RTMP/HTTP)</div>
        <input id="stream_url" class="input" placeholder="rtmp://... or https://..." />
        <div class="row2">
          <button class="k-blue" onclick="connectStream()">Connect</button>
          <button class="k-gray" onclick="send('disconnect')">Disconnect</button>
        </div>
      </div>

      <div id="pane-light" class="pane">
        <div class="label">Presets</div>
        <div class="preset-row">
          <button class="k-gray" onclick="applyPreset('low_light')">Low Light</button>
          <button class="k-gray" onclick="applyPreset('natural')">Natural</button>
          <button class="k-gray" onclick="applyPreset('sharp')">Sharp</button>
        </div>
        <div class="label">Custom Preset Name</div>
        <input id="preset_name" class="input" placeholder="e.g. doc_scan_night" />
        <div class="preset-tools">
          <button class="k-blue" onclick="savePreset()">Save Current</button>
          <button class="k-gray" onclick="reloadPresets()">Reload Presets</button>
        </div>
        <div id="custom_preset_list" class="preset-list"></div>
        <div id="custom_preset_actions" class="preset-list-actions"></div>
        <div class="label">Rename Preset</div>
        <input id="rename_from" class="input" placeholder="old name" />
        <input id="rename_to" class="input" placeholder="new name" />
        <div class="preset-tools">
          <button class="k-orange" onclick="renamePreset()">Rename</button>
          <button class="k-gray" onclick="exportPresets()">Export JSON</button>
        </div>
        <div class="label">Import / Export JSON</div>
        <textarea id="preset_json" class="textarea" placeholder='{"my_preset":{"brightness":10,"contrast":0,"sharpness":20,"light_intensity":50}}'></textarea>
        <div class="preset-tools">
          <button class="k-blue" onclick="importPresets()">Import JSON</button>
          <button class="k-gray" onclick="copyPresetJson()">Copy JSON</button>
        </div>
        <div class="label">Brightness: <span id="v-brightness">0</span></div>
        <input id="brightness" type="range" min="-100" max="100" value="0" oninput="setSlider('brightness', this.value)">
        <div class="label">Contrast: <span id="v-contrast">0</span></div>
        <input id="contrast" type="range" min="-100" max="100" value="0" oninput="setSlider('contrast', this.value)">
        <div class="label">Sharpness: <span id="v-sharpness">0</span></div>
        <input id="sharpness" type="range" min="0" max="100" value="0" oninput="setSlider('sharpness', this.value)">
        <div class="label">Light Intensity: <span id="v-light_intensity">50</span></div>
        <input id="light_intensity" type="range" min="0" max="100" value="50" oninput="setSlider('light_intensity', this.value)">
        <div class="row2">
          <button class="k-gray" onclick="send('light_reset')">Reset Defaults</button>
          <button onclick="refreshState()">Refresh</button>
        </div>
      </div>
    </div>
    <div class="tiny">Tip: Add this page to iPhone Home Screen. This panel is separate and does not inject into target apps.</div>
    <a class="audit-link" href="/control/audit-ui">Open action history</a>
  </div>
  <script>
    function openTab(name) {
      const tabs = ['control', 'source', 'light'];
      tabs.forEach(t => {
        document.getElementById('tab-' + t).classList.toggle('active', t === name);
        document.getElementById('pane-' + t).classList.toggle('active', t === name);
      });
    }
    async function refreshState() {
      const r = await fetch('/control/state');
      const s = await r.json();
      document.getElementById('state').textContent = `x: ${s.x} | y: ${s.y} | zoom: ${s.zoom.toFixed(2)}x | source: ${s.source} | preset: ${s.preset} | connected: ${s.connected ? 'yes' : 'no'}`;
      document.getElementById('stream_url').value = s.stream_url || '';
      ['brightness','contrast','sharpness','light_intensity'].forEach(k => {
        const el = document.getElementById(k);
        const v = document.getElementById('v-' + k);
        if (el) el.value = s[k];
        if (v) v.textContent = s[k];
      });
      reloadPresets();
    }
    async function send(action) {
      await fetch('/control/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action})
      });
      refreshState();
    }
    async function connectStream() {
      const streamUrl = document.getElementById('stream_url').value.trim();
      await fetch('/control/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'connect', stream_url: streamUrl})
      });
      refreshState();
    }
    async function setSlider(key, value) {
      document.getElementById('v-' + key).textContent = value;
      await fetch('/control/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'set_value', key, value: Number(value)})
      });
    }
    async function applyPreset(name) {
      await fetch('/control/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'apply_preset', preset: name})
      });
      refreshState();
    }
    async function savePreset() {
      const name = document.getElementById('preset_name').value.trim();
      if (!name) return;
      await fetch('/control/preset/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
      });
      document.getElementById('preset_name').value = '';
      reloadPresets();
      refreshState();
    }
    async function deletePreset(name) {
      await fetch('/control/preset/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
      });
      reloadPresets();
      refreshState();
    }
    async function renamePreset() {
      const oldName = document.getElementById('rename_from').value.trim();
      const newName = document.getElementById('rename_to').value.trim();
      if (!oldName || !newName) return;
      await fetch('/control/preset/rename', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({old_name: oldName, new_name: newName})
      });
      document.getElementById('rename_from').value = '';
      document.getElementById('rename_to').value = '';
      reloadPresets();
      refreshState();
    }
    async function exportPresets() {
      const r = await fetch('/control/preset/export');
      const data = await r.json();
      document.getElementById('preset_json').value = JSON.stringify(data.presets || {}, null, 2);
    }
    async function importPresets() {
      const text = document.getElementById('preset_json').value.trim();
      if (!text) return;
      let parsed;
      try {
        parsed = JSON.parse(text);
      } catch (e) {
        alert('Invalid JSON');
        return;
      }
      await fetch('/control/preset/import', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({presets: parsed})
      });
      reloadPresets();
    }
    async function copyPresetJson() {
      const text = document.getElementById('preset_json').value;
      if (!text) return;
      await navigator.clipboard.writeText(text);
    }
    async function reloadPresets() {
      const r = await fetch('/control/presets');
      const data = await r.json();
      const presets = data.presets || {};
      const box = document.getElementById('custom_preset_list');
      const boxActions = document.getElementById('custom_preset_actions');
      const staticNames = ['low_light','natural','sharp'];
      const customNames = Object.keys(presets).filter(n => !staticNames.includes(n));
      if (!customNames.length) {
        box.innerHTML = '';
        boxActions.innerHTML = '';
        return;
      }
      box.innerHTML = customNames.map(name => `
        <button class="k-purple" onclick="applyPreset('${name}')">${name}</button>
      `).join('');
      boxActions.innerHTML = customNames.map(name => `
        <button class="k-red" onclick="deletePreset('${name}')">Del ${name}</button>
      `).join('');
    }
    refreshState();
  </script>
</body>
</html>"""

    @app.get("/control/audit-ui", response_class=HTMLResponse)
    async def audit_page() -> str:
        return """<!doctype html>
<html lang="en">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta charset="utf-8">
  <title>VietVCam Audit</title>
  <style>
    body { font-family: -apple-system, Arial, sans-serif; margin: 0; background: #071024; color: #eef2ff; }
    .wrap { max-width: 460px; margin: 0 auto; padding: 14px; }
    .title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .sub { font-size: 12px; opacity: .82; margin-bottom: 10px; }
    .row { display: flex; gap: 8px; margin-bottom: 10px; }
    button { border: 0; border-radius: 9px; padding: 9px 10px; font-size: 13px; font-weight: 700; color: #fff; background: #2282ff; }
    .btn-gray { background: #6b7280; }
    .list { display: grid; gap: 8px; }
    .item { background: #1f2a44; border: 1px solid #374151; border-radius: 10px; padding: 8px; }
    .meta { font-size: 11px; opacity: .8; margin-top: 4px; }
    a { color: #93c5fd; text-decoration: none; font-size: 12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="title">VietVCam Action History</div>
    <div class="sub">Latest 200 actions from operator panel</div>
    <div class="row">
      <button onclick="refreshAudit()">Refresh</button>
      <button class="btn-gray" onclick="clearAudit()">Clear List</button>
    </div>
    <div id="list" class="list"></div>
    <div style="margin-top: 10px;"><a href="/control">Back to Control</a></div>
  </div>
  <script>
    function fmt(ts) {
      return new Date(ts * 1000).toLocaleString();
    }
    async function refreshAudit() {
      const r = await fetch('/control/audit');
      const data = await r.json();
      const items = data.items || [];
      const list = document.getElementById('list');
      if (!items.length) {
        list.innerHTML = '<div class="item">No actions yet.</div>';
        return;
      }
      const html = items.slice().reverse().map(i => `
        <div class="item">
          <div><b>${i.action}</b>${i.detail ? ` - ${i.detail}` : ''}</div>
          <div class="meta">${fmt(i.ts)} | x:${i.x} y:${i.y} zoom:${Number(i.zoom).toFixed(2)} source:${i.source} connected:${i.connected ? 'yes' : 'no'}</div>
        </div>
      `).join('');
      list.innerHTML = html;
    }
    async function clearAudit() {
      await fetch('/control/audit/clear', { method: 'POST' });
      refreshAudit();
    }
    refreshAudit();
  </script>
</body>
</html>"""

    @app.get("/control/state")
    async def get_control_state() -> dict[str, float | int | bool | str]:
        return store.snapshot()

    @app.get("/control/presets")
    async def list_presets() -> dict[str, dict[str, dict[str, int | str]]]:
        merged = dict(PRESETS)
        merged.update(custom_presets)
        return {"presets": merged}

    @app.post("/control/preset/save")
    async def save_custom_preset(payload: dict[str, str]) -> dict[str, str]:
        raw_name = str(payload.get("name", ""))
        if not raw_name.strip():
            raise HTTPException(status_code=400, detail="preset name is required")
        safe_name = _sanitize_preset_name(raw_name)
        if not safe_name:
            raise HTTPException(status_code=400, detail="invalid preset name")
        if safe_name in PRESETS:
            raise HTTPException(status_code=400, detail="preset name is reserved")
        snap = store.snapshot()
        custom_presets[safe_name] = {
            "brightness": int(snap["brightness"]),
            "contrast": int(snap["contrast"]),
            "sharpness": int(snap["sharpness"]),
            "light_intensity": int(snap["light_intensity"]),
            "preset": safe_name,
        }
        _save_custom_presets()
        _append_audit("save_preset", safe_name)
        return {"ok": "true", "name": safe_name}

    @app.post("/control/preset/rename")
    async def rename_custom_preset(payload: dict[str, str]) -> dict[str, str]:
        old_name = _sanitize_preset_name(str(payload.get("old_name", "")))
        new_name = _sanitize_preset_name(str(payload.get("new_name", "")))
        if not old_name or not new_name:
            raise HTTPException(status_code=400, detail="old_name and new_name are required")
        if old_name not in custom_presets:
            raise HTTPException(status_code=404, detail="old preset not found")
        if new_name in PRESETS:
            raise HTTPException(status_code=400, detail="new preset name is reserved")
        preset_values = dict(custom_presets[old_name])
        preset_values["preset"] = new_name
        if new_name != old_name and new_name in custom_presets:
            raise HTTPException(status_code=400, detail="new preset already exists")
        del custom_presets[old_name]
        custom_presets[new_name] = preset_values
        _save_custom_presets()
        _append_audit("rename_preset", f"{old_name}->{new_name}")
        return {"ok": "true", "name": new_name}

    @app.post("/control/preset/delete")
    async def delete_custom_preset(payload: dict[str, str]) -> dict[str, str]:
        name = _sanitize_preset_name(str(payload.get("name", "")))
        if name in custom_presets:
            del custom_presets[name]
            _save_custom_presets()
            _append_audit("delete_preset", name)
        return {"ok": "true"}

    @app.get("/control/preset/export")
    async def export_custom_presets() -> dict[str, dict[str, dict[str, int | str]]]:
        return {"presets": dict(custom_presets)}

    @app.post("/control/preset/import")
    async def import_custom_presets(
        payload: dict[str, dict[str, dict[str, int | str]]],
    ) -> dict[str, int | str]:
        incoming = payload.get("presets")
        if not isinstance(incoming, dict):
            raise HTTPException(status_code=400, detail="presets object is required")
        imported_count = 0
        for raw_name, raw_values in incoming.items():
            if not isinstance(raw_values, dict):
                continue
            safe_name = _sanitize_preset_name(str(raw_name))
            if not safe_name or safe_name in PRESETS:
                continue
            custom_presets[safe_name] = {
                "brightness": int(raw_values.get("brightness", 0)),
                "contrast": int(raw_values.get("contrast", 0)),
                "sharpness": int(raw_values.get("sharpness", 0)),
                "light_intensity": int(raw_values.get("light_intensity", 50)),
                "preset": safe_name,
            }
            imported_count += 1
        _save_custom_presets()
        _append_audit("import_presets", str(imported_count))
        return {"ok": "true", "imported": imported_count}

    @app.get("/control/audit")
    async def get_audit() -> dict[str, list[dict[str, str | int | float | bool]]]:
        return {"items": list(audit_log)}

    @app.post("/control/audit/clear")
    async def clear_audit() -> dict[str, str]:
        audit_log.clear()
        return {"ok": "true"}

    @app.post("/control/move")
    async def control_move(payload: dict[str, str | int | float]) -> dict[str, float | int | bool | str]:
        action = payload.get("action", "")

        def apply(state: dict[str, str | int | float | bool]) -> None:
            if action == "left":
                state["x"] = int(state["x"]) - 10
            elif action == "right":
                state["x"] = int(state["x"]) + 10
            elif action == "up":
                state["y"] = int(state["y"]) - 10
            elif action == "down":
                state["y"] = int(state["y"]) + 10
            elif action == "zoom_in":
                state["zoom"] = min(4.0, float(state["zoom"]) + 0.1)
            elif action == "zoom_out":
                state["zoom"] = max(0.2, float(state["zoom"]) - 0.1)
            elif action == "reset":
                state["x"] = 0
                state["y"] = 0
                state["zoom"] = 1.0
            elif action == "source_1":
                state["source"] = 1
            elif action == "source_2":
                state["source"] = 2
            elif action == "source_3":
                state["source"] = 3
            elif action == "source_4":
                state["source"] = 4
            elif action == "source_5":
                state["source"] = 5
            elif action == "source_6":
                state["source"] = 6
            elif action == "pause":
                state["paused"] = not bool(state["paused"])
            elif action == "play":
                state["paused"] = False
            elif action == "clear":
                state["x"] = 0
                state["y"] = 0
            elif action == "select":
                pass
            elif action == "connect":
                stream_url = str(payload.get("stream_url", "")).strip()
                state["stream_url"] = stream_url
                state["connected"] = bool(stream_url)
                _append_audit("connect", stream_url)
            elif action == "disconnect":
                state["connected"] = False
            elif action == "disable_vcam":
                state["paused"] = True
                state["connected"] = False
            elif action == "hide":
                pass
            elif action == "close":
                state["paused"] = True
            elif action == "set_value":
                key = str(payload.get("key", "")).strip()
                value = payload.get("value")
                if key in {"brightness", "contrast", "sharpness", "light_intensity"}:
                    state[key] = int(float(value))  # type: ignore[arg-type]
                    state["preset"] = "custom"
            elif action == "light_reset":
                state["brightness"] = 0
                state["contrast"] = 0
                state["sharpness"] = 0
                state["light_intensity"] = 50
                state["preset"] = "natural"
            elif action == "apply_preset":
                preset_name = str(payload.get("preset", "")).strip()
                preset = PRESETS.get(preset_name) or custom_presets.get(preset_name)
                if preset:
                    for k, v in preset.items():
                        state[k] = v

        snapshot = store.mutate(apply)
        _append_audit(str(action))
        logger.info(
            "control action=%s x=%s y=%s zoom=%.2f source=%s connected=%s",
            action,
            snapshot["x"],
            snapshot["y"],
            snapshot["zoom"],
            snapshot["source"],
            snapshot["connected"],
        )
        return snapshot

    @app.post("/upload")
    async def upload_video(
        file: UploadFile = File(...),
        x_upload_token: str | None = Header(default=None),
    ) -> dict[str, str | int]:
        if settings.upload_token and x_upload_token != settings.upload_token:
            raise HTTPException(status_code=401, detail="invalid upload token")

        content_type = (file.content_type or "").lower()
        if not (
            content_type.startswith("video/")
            or content_type.startswith("image/")
            or content_type == "application/octet-stream"
        ):
            raise HTTPException(
                status_code=415,
                detail="only image/video uploads are allowed",
            )

        suffix = _safe_suffix(file.filename or "")
        target = settings.upload_dir / f"{uuid4().hex}{suffix}"
        max_bytes = settings.max_upload_mb * 1024 * 1024
        written = 0

        with target.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    out.close()
                    target.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"file exceeds {settings.max_upload_mb} MB",
                    )
                out.write(chunk)

        logger.info("uploaded file=%s size=%s", target.name, written)
        return {"ok": "true", "filename": target.name, "bytes": written}

    return app
