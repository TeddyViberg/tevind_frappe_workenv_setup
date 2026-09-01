#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="pip"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

PIP_MIN="25.3"

with_uv_path

if ! command -v python3 >/dev/null 2>&1; then
  log "ERROR: python3 is not installed. Run scripts/upgrades/python.sh first."
  exit 1
fi

log "Upgrading pip to >= ${PIP_MIN}..."
python3 -m pip install --upgrade "pip>=${PIP_MIN}"
log "Done: $(python3 -m pip --version)"
