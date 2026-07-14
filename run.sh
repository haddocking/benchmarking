#!/usr/bin/env bash
#===============================================================================
# run.sh — convenience wrapper around haddock-runner.
#
# haddock-runner needs `haddock3` on PATH (from the repo's .venv) and expects
# to be invoked from the repository root (scenario YAMLs use paths relative
# to their own directory). This activates the venv, puts binaries/ (uv,
# haddock-runner) on PATH, and execs haddock-runner with your arguments -
# no manual `source .venv/bin/activate` needed.
#
# Usage:
#   ./run.sh Docking_benchmarks/<System>/<scenario>.yaml
#   nohup ./run.sh <scenario.yaml> > run.out & disown && tail -f run.out
#===============================================================================
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh" # sets VENV_PATH, exports PATH with binaries/

if [ $# -eq 0 ]; then
  echo "Usage: $0 <scenario.yaml> [haddock-runner args...]" >&2
  exit 1
fi

if [ ! -x "$VENV_PATH/bin/haddock3" ]; then
  echo "[!!] haddock3 not found in $VENV_PATH - run ./setup.sh first" >&2
  exit 1
fi
if [ ! -x "$BIN_DIR/haddock-runner" ]; then
  echo "[!!] haddock-runner not found in $BIN_DIR - run ./setup.sh first" >&2
  exit 1
fi
source "$VENV_PATH/bin/activate"

exec "$BIN_DIR/haddock-runner" "$@"
