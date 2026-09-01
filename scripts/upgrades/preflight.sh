#!/usr/bin/env bash
set -euo pipefail

UPGRADE_NAME="preflight"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

log "Updating package index..."
sudo apt-get update
