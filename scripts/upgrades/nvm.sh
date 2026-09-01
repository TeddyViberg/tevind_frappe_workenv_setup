#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="nvm"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

NVM_VERSION="v0.40.3"
NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh"

if [[ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]]; then
  source_nvm
  log "Already installed: nvm $(nvm --version)"
  exit 0
fi

log "Installing nvm ${NVM_VERSION}..."
curl -o- "$NVM_INSTALL_URL" | bash

source_nvm || true
log "Done: nvm $(nvm --version 2>/dev/null || echo installed)"
