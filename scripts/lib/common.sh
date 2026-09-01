#!/usr/bin/env bash
# Shared helpers for upgrade scripts.

log() {
  echo "[${UPGRADE_NAME:-upgrade}] $*"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "ERROR: required command not found: $1"
    exit 1
  fi
}

apt_install() {
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
}

source_nvm() {
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [[ -s "$NVM_DIR/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
    return 0
  fi
  return 1
}

with_uv_path() {
  export PATH="$HOME/.local/bin:$PATH"
}
