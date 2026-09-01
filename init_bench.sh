#!/usr/bin/env bash
# Standalone script to initialize a Frappe v16 bench, site, and tevind_studio app.
#
# Prerequisites:
#   - bench CLI (uv tool install frappe-bench)
#   - Python 3.14 via uv
#   - MariaDB with user 'frappe' and password you set during install
#   - SSH access to git@github.com:TeddyViberg/tevind_studio.git
#
# Usage:
#   ./init_bench.sh
#   ./init_bench.sh --help
#
# Environment overrides:
#   BENCH_DIR, BENCH_NAME, SITE_NAME, FRAPPE_BRANCH, APP_REPO, APP_BRANCH, APP_NAME, DB_ROOT_USER, PYTHON
set -euo pipefail

BENCH_DIR="${BENCH_DIR:-}"
BENCH_NAME="${BENCH_NAME:-tevind_bench}"
SITE_NAME="${SITE_NAME:-tevind.localhost}"
FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-16}"
APP_REPO="${APP_REPO:-git@github.com:TeddyViberg/tevind_studio.git}"
APP_BRANCH="${APP_BRANCH:-master}"
APP_NAME="${APP_NAME:-tevind_studio}"
DB_ROOT_USER="${DB_ROOT_USER:-frappe}"

export PATH="${HOME}/.local/bin:${PATH}"

log() { echo "[init-bench] $*"; }
die() { echo "[init-bench] ERROR: $*" >&2; exit 1; }

usage() {
  cat <<EOF
Initialize a Frappe v16 bench with tevind_studio.

Usage: $0 [options]

Options:
  -d, --directory DIR  Parent directory for the bench (prompted if omitted)
  --bench-name NAME    Bench folder name (default: tevind_bench)
  --site NAME          Site name (default: tevind.localhost)
  --frappe-branch BR   Frappe branch (default: version-16)
  --app-repo URL       Git repo URL (default: TeddyViberg/tevind_studio)
  --app-branch BR      App branch (default: master)
  --app-name NAME      App name for install-app (default: tevind_studio)
  --db-user USER       MariaDB admin user (default: frappe)
  --python PATH        Python 3.14 binary (auto-detected if omitted)
  -h, --help           Show this help

You will be prompted for the MariaDB password for user '${DB_ROOT_USER}'.

Examples:
  $0
  $0 -d /home/user/projects
  $0 -d ~/Work --bench-name tevind_bench
EOF
}

resolve_python() {
  if [[ -n "${PYTHON:-}" && -x "${PYTHON}" ]]; then
    echo "$PYTHON"
    return 0
  fi

  if command -v uv >/dev/null 2>&1; then
    local uv_python
    uv_python="$(uv python find 3.14 2>/dev/null || true)"
    if [[ -n "$uv_python" && -x "$uv_python" ]]; then
      echo "$uv_python"
      return 0
    fi
  fi

  local candidates=(
    "${HOME}/.local/share/uv/python/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
    "${HOME}/.local/bin/python3.14"
  )
  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done

  die "Python 3.14 not found. Install with: uv python install 3.14 --default"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -d|--directory) BENCH_DIR="$2"; shift 2 ;;
      --bench-name) BENCH_NAME="$2"; shift 2 ;;
      --site) SITE_NAME="$2"; shift 2 ;;
      --frappe-branch) FRAPPE_BRANCH="$2"; shift 2 ;;
      --app-repo) APP_REPO="$2"; shift 2 ;;
      --app-branch) APP_BRANCH="$2"; shift 2 ;;
      --app-name) APP_NAME="$2"; shift 2 ;;
      --db-user) DB_ROOT_USER="$2"; shift 2 ;;
      --python) PYTHON="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "Unknown option: $1 (try --help)" ;;
    esac
  done
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "'$1' not found in PATH"
}

prompt_db_password() {
  if [[ -n "${DB_ROOT_PASSWORD:-}" ]]; then
    return 0
  fi
  echo ""
  echo "Enter MariaDB password for user '${DB_ROOT_USER}'"
  echo "(the password you set when MariaDB was installed):"
  read -rs DB_ROOT_PASSWORD
  echo ""
  if [[ -z "$DB_ROOT_PASSWORD" ]]; then
    die "Password cannot be empty"
  fi
}

resolve_bench_dir() {
  if [[ -z "$BENCH_DIR" ]]; then
    echo ""
    read -rp "Enter directory where the bench should be created (default: ${PWD}): " input
    BENCH_DIR="${input:-$PWD}"
  fi

  BENCH_DIR="${BENCH_DIR/#\~/$HOME}"

  if [[ ! -d "$BENCH_DIR" ]]; then
    log "Creating directory: $BENCH_DIR"
    mkdir -p "$BENCH_DIR"
  fi

  BENCH_DIR="$(cd "$BENCH_DIR" && pwd)"
  BENCH_PATH="$BENCH_DIR/$BENCH_NAME"
}

init_bench() {
  if [[ -d "$BENCH_PATH" ]]; then
    die "Bench directory already exists: $BENCH_PATH"
  fi

  local python_bin
  python_bin="$(resolve_python)"
  log "Using Python: $python_bin"
  log "Bench path: $BENCH_PATH"

  cd "$BENCH_DIR"
  log "Initializing bench '$BENCH_NAME' (frappe-branch: $FRAPPE_BRANCH)..."
  bench init "$BENCH_NAME" \
    --frappe-branch "$FRAPPE_BRANCH" \
    --python "$python_bin"
}

create_site() {
  log "Creating site '$SITE_NAME'..."
  bench new-site "$SITE_NAME" \
    --db-root-username "$DB_ROOT_USER" \
    --db-root-password "$DB_ROOT_PASSWORD"
}

get_app() {
  if [[ -d "apps/$APP_NAME" ]]; then
    log "App '$APP_NAME' already present in apps/, skipping get-app"
    return 0
  fi

  log "Fetching app from $APP_REPO (branch: $APP_BRANCH)..."
  bench get-app "$APP_REPO" --branch "$APP_BRANCH"
}

install_app() {
  log "Installing app '$APP_NAME' on site '$SITE_NAME'..."
  bench --site "$SITE_NAME" install-app "$APP_NAME"
}

main() {
  parse_args "$@"

  require_command bench

  resolve_bench_dir
  prompt_db_password

  init_bench
  cd "$BENCH_PATH"

  create_site
  get_app
  install_app

  echo ""
  log "Done!"
  echo "  Bench:  $BENCH_PATH"
  echo "  Site:   $SITE_NAME"
  echo "  App:    $APP_NAME"
  echo ""
  echo "Start the dev server:"
  echo "  cd $BENCH_PATH && bench start"
  echo ""
  echo "Open in browser:"
  echo "  http://${SITE_NAME}:8000"
}

main "$@"
