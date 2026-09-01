#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="node"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

NODE_VERSION="24"

if ! source_nvm; then
  log "ERROR: nvm is not installed. Run scripts/upgrades/nvm.sh first."
  exit 1
fi

CURRENT="$(node -v 2>/dev/null || true)"
if [[ "$CURRENT" == "v${NODE_VERSION}"* ]] || [[ "$CURRENT" == "v24"* ]]; then
  log "Already on Node ${CURRENT}"
  exit 0
fi

log "Installing Node.js ${NODE_VERSION}..."
nvm install "$NODE_VERSION"
nvm use "$NODE_VERSION" 2>/dev/null || true

log "Done: $(node -v)"
