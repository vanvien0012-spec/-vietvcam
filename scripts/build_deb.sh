#!/usr/bin/env bash
set -euo pipefail

APP_NAME="vietvcam"
VERSION="1.0.0"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_DIR="${ROOT_DIR}/build/${APP_NAME}_${VERSION}"
DIST_DIR="${ROOT_DIR}/dist"

echo "==> Preparing package tree"
rm -rf "${PKG_DIR}"
mkdir -p "${PKG_DIR}/DEBIAN"
mkdir -p "${PKG_DIR}/opt/${APP_NAME}"
mkdir -p "${PKG_DIR}/usr/local/bin"
mkdir -p "${PKG_DIR}/usr/lib/systemd/system"

echo "==> Copying application sources"
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'build' \
  --exclude 'dist' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  "${ROOT_DIR}/" "${PKG_DIR}/opt/${APP_NAME}/"

echo "==> Installing package metadata"
chmod 755 "${PKG_DIR}/DEBIAN"
cp "${ROOT_DIR}/packaging/debian/control" "${PKG_DIR}/DEBIAN/control"
cp "${ROOT_DIR}/packaging/debian/postinst" "${PKG_DIR}/DEBIAN/postinst"
cp "${ROOT_DIR}/packaging/debian/prerm" "${PKG_DIR}/DEBIAN/prerm"
cp "${ROOT_DIR}/packaging/debian/vietvcam" "${PKG_DIR}/usr/local/bin/vietvcam"
cp "${ROOT_DIR}/packaging/debian/vietvcam.service" \
  "${PKG_DIR}/usr/lib/systemd/system/vietvcam.service"

chmod 755 "${PKG_DIR}/DEBIAN/postinst" "${PKG_DIR}/DEBIAN/prerm"
chmod 755 "${PKG_DIR}/usr/local/bin/vietvcam"

mkdir -p "${DIST_DIR}"
echo "==> Building .deb"
dpkg-deb --build "${PKG_DIR}" "${DIST_DIR}/${APP_NAME}_${VERSION}_all.deb"

echo "Done: ${DIST_DIR}/${APP_NAME}_${VERSION}_all.deb"
