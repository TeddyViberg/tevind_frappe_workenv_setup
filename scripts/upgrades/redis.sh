#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="redis"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

log "Installing redis-server..."
apt_install redis-server
log "Done: $(redis-server --version)"
