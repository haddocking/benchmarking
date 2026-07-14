#!/usr/bin/env bash
#
# Wrapper around analysis/AnalyseBenchmarkResults.py: runs it with the
# venv's python3 so numpy/matplotlib are there without activating anything.
#
# Usage:
#   ./analyse.sh <benchmark_results_dir> [options]
#   ./analyse.sh results/protein-protein/ -t protein -m irmsd
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <benchmark_results_dir> [options]" >&2
  exit 1
fi

if [ ! -x "$VENV_PATH/bin/python3" ]; then
  echo "[!!] python3 not found in $VENV_PATH - run ./setup.sh first" >&2
  exit 1
fi

exec "$VENV_PATH/bin/python3" "$REPO_ROOT/analysis/AnalyseBenchmarkResults.py" "$@"
