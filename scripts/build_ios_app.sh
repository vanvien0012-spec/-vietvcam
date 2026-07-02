#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IOS_DIR="${ROOT_DIR}/ios"
DIST_DIR="${ROOT_DIR}/dist"

if [ -z "${THEOS:-}" ]; then
  echo "THEOS is not set."
  echo "Install Theos and run:"
  echo "  export THEOS=~/theos"
  echo "  $0"
  exit 1
fi

if [ ! -d "${THEOS}" ]; then
  echo "THEOS path not found: ${THEOS}"
  exit 1
fi

echo "==> Building iOS app package with Theos"
pushd "${IOS_DIR}" >/dev/null
make clean package
popd >/dev/null

mkdir -p "${DIST_DIR}"
LATEST="$(ls -1t "${IOS_DIR}"/packages/com.vanvi.vietvcam_*.deb 2>/dev/null | head -n 1 || true)"
if [ -z "${LATEST}" ]; then
  echo "No iOS package found in ios/packages/"
  exit 1
fi

cp -f "${LATEST}" "${DIST_DIR}/"
echo "Done: ${DIST_DIR}/$(basename "${LATEST}")"
echo "Next: ./scripts/build_sileo_repo.sh"
