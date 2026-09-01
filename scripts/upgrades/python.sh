#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="python"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

PYTHON_VERSION="3.14"

with_uv_path

if ! command -v uv >/dev/null 2>&1; then
  log "ERROR: uv is not installed. Run scripts/upgrades/uv.sh first."
  exit 1
fi

CURRENT="$(python3 --version 2>/dev/null || true)"
if [[ "$CURRENT" == "Python ${PYTHON_VERSION}"* ]]; then
  log "Already on ${CURRENT}"
  exit 0
fi

log "Installing Python ${PYTHON_VERSION}..."
uv python install "$PYTHON_VERSION" --default
log "Done: $(python3 --version)"
