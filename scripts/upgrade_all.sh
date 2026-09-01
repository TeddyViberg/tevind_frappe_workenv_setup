#!/usr/bin/env bash
# Run all dependency upgrade scripts in order, or a single one by name.
#
# Usage:
#   ./scripts/upgrade_all.sh              # upgrade everything
#   ./scripts/upgrade_all.sh mariadb      # upgrade one dependency
#   ./scripts/upgrade_all.sh --list       # list available dependencies
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
UPGRADES_DIR="$SCRIPTS_DIR/upgrades"

# Order matters: nvm before node/yarn, uv before python/pip/bench
ALL_UPGRADES=(
  preflight
  git
  mariadb
  redis
  wkhtmltopdf
  nvm
  node
  yarn
  uv
  python
  pip
  bench
)

list_upgrades() {
  echo "Available upgrades:"
  for name in "${ALL_UPGRADES[@]}"; do
    [[ "$name" == "preflight" ]] && continue
    echo "  $name"
  done
}

usage() {
  echo "Usage: $0 [--list] [dependency ...]"
  echo ""
  list_upgrades
}

run_upgrade() {
  local name="$1"
  local script="$UPGRADES_DIR/${name}.sh"

  if [[ ! -f "$script" ]]; then
    echo "ERROR: no upgrade script for '$name' (expected $script)" >&2
    return 1
  fi

  echo ""
  echo "========================================"
  echo " Running upgrade: $name"
  echo "========================================"
  bash "$script"
}

if [[ "${1:-}" == "--list" ]]; then
  list_upgrades
  exit 0
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  TARGETS=("$@")
else
  TARGETS=("${ALL_UPGRADES[@]}")
fi

FAILED=()
for name in "${TARGETS[@]}"; do
  if ! run_upgrade "$name"; then
    FAILED+=("$name")
  fi
done

echo ""
if [[ ${#FAILED[@]} -eq 0 ]]; then
  echo "All upgrades completed successfully."
  exit 0
fi

echo "Failed upgrades: ${FAILED[*]}"
exit 1
