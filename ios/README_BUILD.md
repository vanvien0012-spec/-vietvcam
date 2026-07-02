# VietVCam iOS (Rootless)

Standalone iPhone app for jailbroken rootless devices.

## Features (1, 2, 4)

1. Runs as its own app icon (not Safari)
2. RTMP / stream URL input in Source tab
4. Control + Light tabs (move, zoom, brightness, contrast, sharpness)

## Requirements

- Jailbroken iPhone (rootless: Dopamine, palera1n rootless, etc.)
- Mac or Linux with [Theos](https://theos.dev) installed
- iOS SDK

## Build on Mac/Linux

```bash
export THEOS=~/theos
cd ios
make clean
make package
```

Output `.deb` is in `ios/packages/`.

Copy to repo:

```bash
cp packages/com.vanvi.vietvcam_*.deb ../dist/
cd ..
./scripts/build_sileo_repo.sh
```

## Install on iPhone

- Sileo: add your repo and install **VietVCam**
- Or Filza: open the `.deb` file

After install, open app **VietVCam** from home screen.

## RTMP note

iOS `AVPlayer` does not play raw RTMP directly on all streams.
Use one of:

- RTMP URL if your server also exposes HLS (`.m3u8`) — put HLS URL in Source tab
- Or convert RTMP to HLS on server (nginx-rtmp `hls on;`)
- Future: integrate MobileVLCKit for native RTMP

Example HLS URL:
`http://192.168.1.100:8080/hls/cam1.m3u8`

## Config file

`/var/jb/var/mobile/Library/Preferences/com.vanvi.vietvcam.plist`

Stores RTMP URL, zoom, brightness, etc.

## Tabs

- **Control**: left/right/down, zoom +/-, pause, disable
- **Source**: RTMP/HLS URL, Connect, Disconnect
- **Light**: brightness, contrast, sharpness, intensity sliders
