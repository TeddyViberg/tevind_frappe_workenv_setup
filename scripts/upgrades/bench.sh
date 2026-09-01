#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="bench"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

with_uv_path

if ! command -v uv >/dev/null 2>&1; then
  log "ERROR: uv is not installed. Run scripts/upgrades/uv.sh first."
  exit 1
fi

if command -v bench >/dev/null 2>&1; then
  log "Already installed: bench $(bench --version)"
  exit 0
fi

log "Installing frappe-bench..."
uv tool install frappe-bench
log "Done: bench $(bench --version)"
