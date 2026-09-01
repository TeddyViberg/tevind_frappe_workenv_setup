#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="uv"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

if command -v uv >/dev/null 2>&1; then
  log "Already installed: $(uv --version)"
  exit 0
fi

log "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
with_uv_path
log "Done: $(uv --version)"
