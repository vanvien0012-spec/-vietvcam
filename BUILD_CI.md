# Build iOS package with GitHub Actions (no Mac needed)

## 1) Push project to GitHub

```bash
git init
git add .
git commit -m "Add VietVCam iOS app and CI"
git remote add origin https://github.com/YOUR_USER/vietvcam.git
git push -u origin main
```

## 2) Run workflow

1. Open GitHub repo -> **Actions**
2. Select workflow **Build VietVCam iOS**
3. Click **Run workflow**

Or push any change under `ios/` to trigger automatically.

## 3) Download artifacts

After workflow finishes (green check):

- **vietvcam-ios-deb** -> `.deb` file for Sileo/Filza
- **vietvcam-sileo-repo** -> full repo folder (`Packages`, `Release`, ...)

## 4) Install on iPhone

### Option A: Filza
1. Download `vietvcam-ios-deb` zip from Actions
2. Send `.deb` to iPhone
3. Open in Filza -> Install -> Respring

### Option B: Sileo local repo
1. Download `vietvcam-sileo-repo` zip
2. Extract on PC
3. Host folder with Python:
   ```bash
   cd repo-sileo
   python3 -m http.server 8888
   ```
4. On iPhone Sileo add source: `http://<PC_IP>:8888`

## 5) Open app

After install, open **VietVCam** from home screen.

- **Source** tab: enter RTMP/HLS URL -> Connect
- **Control** tab: move/zoom
- **Light** tab: brightness/contrast/sharpness
