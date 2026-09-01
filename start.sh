#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "tkinter is required. Install with: sudo apt install python3-tk"
  exit 1
fi

exec python3 "$ROOT/check_env.py"
