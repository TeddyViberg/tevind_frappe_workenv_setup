#!/usr/bin/env bash
# Upgrade MariaDB to 11.8 on Ubuntu 24.04 / 22.04 via MariaDB.org repository.
# Handles migration from Ubuntu-packaged 10.11 using mariadb-upgrade.
set -euo pipefail

UPGRADE_NAME="mariadb"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

if [[ ! -f /etc/os-release ]]; then
  log "ERROR: /etc/os-release not found"
  exit 1
fi

# shellcheck source=/dev/null
. /etc/os-release
CODENAME="${VERSION_CODENAME:-}"

if [[ -z "$CODENAME" ]]; then
  log "ERROR: cannot detect OS codename"
  exit 1
fi

log "OS: ${NAME:-unknown} ${VERSION_ID:-} (${CODENAME})"

apt_install curl ca-certificates gnupg apt-transport-https

# Remove all stale MariaDB apt source files (failed installs often leave empty duplicates)
sudo rm -f /etc/apt/sources.list.d/mariadb.sources \
           /etc/apt/sources.list.d/mariadb.list \
           /etc/apt/sources.list.d/mariadb.sources.old_*.disabled

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://mariadb.org/mariadb_release_signing_key.pgp \
  | sudo gpg --dearmor --yes -o /etc/apt/keyrings/mariadb-keyring.gpg

log "Adding MariaDB 11.8 repository for suite: ${CODENAME}"
printf '%s\n' \
  'X-Repolib-Name: MariaDB' \
  'Types: deb' \
  'URIs: https://deb.mariadb.org/11.8/ubuntu' \
  "Suites: ${CODENAME}" \
  'Components: main' \
  'Signed-By: /etc/apt/keyrings/mariadb-keyring.gpg' \
  | sudo tee /etc/apt/sources.list.d/mariadb.sources > /dev/null

sudo apt-get update

CANDIDATE="$(apt-cache policy mariadb-server 2>/dev/null | awk '/Candidate:/ {print $2}')"
log "mariadb-server candidate: ${CANDIDATE}"

if [[ -z "$CANDIDATE" ]] || [[ "$CANDIDATE" != *"11.8"* ]]; then
  log "ERROR: MariaDB 11.8 is not the apt candidate."
  log "Check /etc/apt/sources.list.d/mariadb.sources and keyring."
  apt-cache policy mariadb-server || true
  exit 1
fi

CURRENT="$(mariadb --version 2>/dev/null || true)"
if [[ "$CURRENT" == *"11.8"* ]]; then
  log "Already on MariaDB 11.8: $CURRENT"
  sudo mariadb-upgrade 2>/dev/null || true
  exit 0
fi

log "Current: ${CURRENT:-not installed}"
log "Stopping MariaDB before upgrade..."
sudo systemctl stop mariadb 2>/dev/null || sudo systemctl stop mysql 2>/dev/null || true

log "Installing MariaDB 11.8 packages (keeping existing config and data)..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  -o Dpkg::Options::="--force-confold" \
  mariadb-server mariadb-client libmariadb-dev pkg-config \
  mariadb-common mysql-common

log "Starting MariaDB..."
sudo systemctl start mariadb
sleep 2

if ! systemctl is-active --quiet mariadb; then
  log "ERROR: MariaDB failed to start. Check: sudo journalctl -xeu mariadb"
  exit 1
fi

log "Running mariadb-upgrade to migrate system tables..."
if sudo mariadb-upgrade; then
  log "mariadb-upgrade completed"
else
  log "WARNING: mariadb-upgrade reported issues — service may still work"
  log "Inspect: sudo journalctl -xeu mariadb"
fi

sudo systemctl restart mariadb
sleep 1

VERSION="$(mariadb --version)"
log "Installed: $VERSION"

if [[ "$VERSION" != *"11.8"* ]]; then
  log "ERROR: upgrade did not reach MariaDB 11.8"
  exit 1
fi

log "MariaDB 11.8 upgrade complete."
