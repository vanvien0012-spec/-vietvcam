#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
DEB_PATH="${ROOT_DIR}/dist/vietvcam_1.0.0_all.deb"

echo "==> Checking required tools"
for cmd in python3 pip3 dpkg-deb rsync; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}"
    echo "Install prerequisites: sudo apt install -y python3 python3-venv python3-pip dpkg-dev rsync ffmpeg"
    exit 1
  fi
done

echo "==> Creating virtual environment if missing"
if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "==> Installing Python dependencies"
pip install -U pip
pip install -e "${ROOT_DIR}" -r "${ROOT_DIR}/requirements-dev.txt"

echo "==> Running quick checks"
python -m compileall "${ROOT_DIR}/src"
pytest -q

echo "==> Building Debian package"
"${ROOT_DIR}/scripts/build_deb.sh"

if [ ! -f "${DEB_PATH}" ]; then
  echo "Build did not produce expected package: ${DEB_PATH}"
  exit 1
fi

echo "==> Installing package"
sudo dpkg -i "${DEB_PATH}" || true
sudo apt -f install -y
sudo dpkg -i "${DEB_PATH}"

echo "==> Restarting and validating service"
sudo systemctl daemon-reload
sudo systemctl restart vietvcam.service
sudo systemctl status vietvcam.service --no-pager
curl -fsS "http://127.0.0.1:8080/health"

echo
echo "Release completed successfully."
echo "Package: ${DEB_PATH}"
