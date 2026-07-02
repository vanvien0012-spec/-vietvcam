#!/usr/bin/env bash
set -euo pipefail

APP_NAME="vietvcam-control"
PKG_ID="com.vanvi.vietvcam"
VERSION="1.0.0"
ARCH="iphoneos-arm64"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${ROOT_DIR}/packaging/sileo-rootless"
BUILD_DIR="${ROOT_DIR}/build/sileo_${APP_NAME}_${VERSION}"
DIST_DIR="${ROOT_DIR}/dist"
OUTPUT_DEB="${DIST_DIR}/${APP_NAME}_${VERSION}_${ARCH}.deb"

echo "==> Preparing Sileo rootless package tree"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
rsync -a "${SRC_DIR}/" "${BUILD_DIR}/"

echo "==> Normalizing permissions"
chmod 755 "${BUILD_DIR}/DEBIAN"
chmod 755 "${BUILD_DIR}/DEBIAN/postinst" "${BUILD_DIR}/DEBIAN/prerm"
chmod 755 "${BUILD_DIR}/var/jb/usr/bin/vietvcam-control"

mkdir -p "${DIST_DIR}"

echo "==> Building Sileo .deb"
dpkg-deb --build "${BUILD_DIR}" "${OUTPUT_DEB}"

echo "Done: ${OUTPUT_DEB}"
echo "Package: ${PKG_ID} ${VERSION} (${ARCH})"
