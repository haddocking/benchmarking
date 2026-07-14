#!/usr/bin/env bash
#
# Wrapper around haddock-runner: activates the venv and calls the binaries/
# copy directly. Run from the repo root, since scenario YAMLs use paths
# relative to themselves.
#
# Usage:
#   ./run.sh docking_benchmarks/<System>/<scenario>.yaml
#   nohup ./run.sh <scenario.yaml> > run.out & disown && tail -f run.out
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh"

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
