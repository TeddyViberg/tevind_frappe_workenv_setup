#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="git"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

log "Installing git..."
apt_install git
log "Done: $(git --version)"
