#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="yarn"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

if ! source_nvm; then
  log "ERROR: nvm is not installed. Run scripts/upgrades/nvm.sh first."
  exit 1
fi

if command -v yarn >/dev/null 2>&1; then
  log "Already installed: yarn $(yarn --version)"
  exit 0
fi

log "Installing yarn..."
npm install -g yarn
log "Done: yarn $(yarn --version)"
