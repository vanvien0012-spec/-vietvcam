#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
REPO_DIR="${ROOT_DIR}/repo-sileo"
POOL_DIR="${REPO_DIR}/pool/main"
DEB_PATTERN="*_iphoneos-arm64.deb"

if ! command -v dpkg-scanpackages >/dev/null 2>&1; then
  echo "Missing dpkg-scanpackages. Install with:"
  echo "  sudo apt install -y dpkg-dev"
  exit 1
fi

mkdir -p "${POOL_DIR}"

LATEST_DEB="$(ls -1t "${DIST_DIR}"/${DEB_PATTERN} 2>/dev/null | head -n 1 || true)"
if [ -z "${LATEST_DEB}" ]; then
  echo "No Sileo package found in ${DIST_DIR} matching ${DEB_PATTERN}"
  echo "Build package first:"
  echo "  ./scripts/build_sileo_deb.sh"
  exit 1
fi

cp -f "${LATEST_DEB}" "${POOL_DIR}/"

pushd "${REPO_DIR}" >/dev/null

echo "==> Generating Packages index"
dpkg-scanpackages --multiversion pool > Packages
gzip -9c Packages > Packages.gz

DATE_RFC2822="$(LC_ALL=C date -R)"
PKG_SIZE="$(wc -c < Packages | tr -d ' ')"
PKG_GZ_SIZE="$(wc -c < Packages.gz | tr -d ' ')"
MD5_PACKAGES="$(md5sum Packages | awk '{print $1}')"
MD5_PACKAGES_GZ="$(md5sum Packages.gz | awk '{print $1}')"
SHA256_PACKAGES="$(sha256sum Packages | awk '{print $1}')"
SHA256_PACKAGES_GZ="$(sha256sum Packages.gz | awk '{print $1}')"

cat > Release <<EOF
Origin: VietVCam
Label: VietVCam
Suite: stable
Version: 1.0
Codename: ios
Architectures: iphoneos-arm64
Components: main
Description: VietVCam Sileo Repository
Date: ${DATE_RFC2822}
MD5Sum:
 ${MD5_PACKAGES} ${PKG_SIZE} Packages
 ${MD5_PACKAGES_GZ} ${PKG_GZ_SIZE} Packages.gz
SHA256:
 ${SHA256_PACKAGES} ${PKG_SIZE} Packages
 ${SHA256_PACKAGES_GZ} ${PKG_GZ_SIZE} Packages.gz
EOF

cat > index.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VietVCam Sileo Repo</title>
  <style>
    body { font-family: -apple-system, Arial, sans-serif; margin: 2rem; line-height: 1.5; }
    code { background: #f4f4f4; padding: 0.15rem 0.35rem; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>VietVCam Sileo Repo</h1>
  <p>Add this URL to Sileo as a source.</p>
  <p>Files available:</p>
  <ul>
    <li><a href="Packages">Packages</a></li>
    <li><a href="Packages.gz">Packages.gz</a></li>
    <li><a href="Release">Release</a></li>
  </ul>
</body>
</html>
EOF

popd >/dev/null

echo "Done: ${REPO_DIR}"
echo "Package indexed: $(basename "${LATEST_DEB}")"
echo
echo "Serve repo:"
echo "  cd \"${REPO_DIR}\" && python3 -m http.server 8888"
echo "Then add source in Sileo:"
echo "  http://<YOUR_PC_IP>:8888"
