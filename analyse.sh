#!/usr/bin/env bash
#===============================================================================
# analyse.sh — convenience wrapper around Analysis/AnalyseBenchmarkResults.py.
#
# The analysis script needs numpy/matplotlib from the repo's .venv. This execs
# it with the venv's python3 directly - no manual `source .venv/bin/activate`
# needed.
#
# Usage:
#   ./analyse.sh <benchmark_results_dir> [options]
#   ./analyse.sh results/protein-protein/ -t protein -m irmsd
#===============================================================================
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh" # sets VENV_PATH, REPO_ROOT

if [ $# -eq 0 ]; then
  echo "Usage: $0 <benchmark_results_dir> [options]" >&2
  exit 1
fi

if [ ! -x "$VENV_PATH/bin/python3" ]; then
  echo "[!!] python3 not found in $VENV_PATH - run ./setup.sh first" >&2
  exit 1
fi

exec "$VENV_PATH/bin/python3" "$REPO_ROOT/Analysis/AnalyseBenchmarkResults.py" "$@"
