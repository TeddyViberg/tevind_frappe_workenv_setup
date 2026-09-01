#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="wkhtmltopdf"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

WKHTML_DEB_URL="https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb"
WKHTML_DEB="/tmp/wkhtmltox.deb"

if command -v wkhtmltopdf >/dev/null 2>&1; then
  log "Already installed: $(wkhtmltopdf --version | head -1)"
  exit 0
fi

log "Installing dependencies..."
apt_install xvfb libfontconfig wget

log "Downloading wkhtmltopdf package..."
wget -q -O "$WKHTML_DEB" "$WKHTML_DEB_URL"

log "Installing wkhtmltopdf package..."
sudo dpkg -i "$WKHTML_DEB" || apt_install -f

log "Done: $(wkhtmltopdf --version | head -1)"
