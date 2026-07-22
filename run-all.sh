#!/usr/bin/env bash
#
# Runs every scenario in the suite, one at a time, via haddock-runner.
# A failing scenario does not abort the rest - this is a benchmark suite,
# partial results still matter.
#
# Usage:
#   ./run-all.sh
#   nohup ./run-all.sh > run-all.out & tail -f run-all.out
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh"

if [ ! -x "$VENV_PATH/bin/haddock3" ]; then
  echo "[!!] haddock3 not found in $VENV_PATH - run ./setup.sh first" >&2
  exit 1
fi
if [ ! -x "$BIN_DIR/haddock-runner" ]; then
  echo "[!!] haddock-runner not found in $BIN_DIR - run ./setup.sh first" >&2
  exit 1
fi
source "$VENV_PATH/bin/activate"

target="${1:-$REPO_ROOT/docking_benchmarks}"
if [[ -f "$target" ]]; then
  scenarios=("$target")
else
  mapfile -t scenarios < <(find "$target" -mindepth 1 -maxdepth 2 -name '*.yaml' | sort)
fi

if [ "${#scenarios[@]}" -eq 0 ]; then
  echo "[!!] No scenario YAMLs found under docking_benchmarks/" >&2
  exit 1
fi

log_dir="$REPO_ROOT/run-all-logs/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$log_dir"

declare -a results=()
failures=0

cd "$REPO_ROOT"
for yaml in "${scenarios[@]}"; do
  system="$(basename "$(dirname "$yaml")")"
  scenario="$(basename "$yaml" .yaml)"
  label="$system/$scenario"
  log_file="$log_dir/${system}_${scenario}.log"

  echo "[+] Running $label"
  if "$BIN_DIR/haddock-runner" "$yaml" >"$log_file" 2>&1; then
    echo "[+] $label done"
    results+=("OK   $label ($log_file)")
  else
    echo "[!!] $label failed - see $log_file"
    results+=("FAIL $label ($log_file)")
    failures=$((failures + 1))
  fi
done

echo
echo "==============================================================="
echo "  Summary ($((${#scenarios[@]} - failures))/${#scenarios[@]} OK)"
echo "---------------------------------------------------------------"
printf '%s\n' "${results[@]}"
echo "==============================================================="

[ "$failures" -eq 0 ]
