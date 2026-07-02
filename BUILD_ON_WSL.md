# Build and run in WSL

Use Ubuntu WSL for packaging:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip dpkg-dev rsync ffmpeg
```

From WSL, move to the project:

```bash
cd /mnt/c/Users/vanvi/Projects/vietvcam
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e . -r requirements-dev.txt
pytest -q
```

Build Debian package:

```bash
chmod +x scripts/build_deb.sh
./scripts/build_deb.sh
```

Install and verify:

```bash
sudo dpkg -i dist/vietvcam_1.0.0_all.deb
sudo systemctl status vietvcam.service --no-pager
curl http://127.0.0.1:8080/health
```

Optional upload token:

```bash
export VIETVCAM_UPLOAD_TOKEN="your_secret_token"
vietvcam --api
```

Hybrid RTMP + upload:

```bash
export VIETVCAM_RTMP_URL="rtmp://YOUR_SERVER/live/stream_key"
export VIETVCAM_UPLOAD_TOKEN="your_secret_token"
vietvcam --hybrid
```

Service config file after install:

```bash
sudo nano /etc/default/vietvcam
sudo systemctl restart vietvcam.service
```
