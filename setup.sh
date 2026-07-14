#!/usr/bin/env bash
#===============================================================================
# Setup: HADDOCK3 + haddock-runner (v3)
#
# Orchestrates independent steps (installs everything LOCALLY, no conda).
# uv and haddock-runner are placed in <repo>/binaries/, not ~/.local/bin, so
# every checkout of this repo carries its own pinned copies:
#   1. scripts/01_python_env.sh     - uv (in binaries/) + Python 3.14 + .venv
#   2. scripts/02_haddock_runner.sh - haddock-runner (prebuilt binary, in binaries/)
#   3. scripts/03_haddock3.sh       - HADDOCK3 + matplotlib + rdkit into .venv
#   4. every Docking_benchmarks/*/setup.sh - stage each benchmark dataset
#
# Each of steps 1-3 is idempotent and can also be run standalone, e.g. to
# reinstall just haddock-runner: bash scripts/02_haddock_runner.sh
#
# All benchmark datasets are staged by default (step 4) - each is quick to
# fetch, so there's no opt-in flag. Output from each dataset's setup.sh is
# logged to Docking_benchmarks/<System>/.log instead of stdout.
#
# Scenario YAMLs use plain relative paths for input_list/work_dir (resolved
# by haddock-runner itself, relative to the YAML file's own directory) - no
# path-substitution step is needed.
#
# Authors: BonvinLab, Computational Structural Biology group,
#          Utrecht University, the Netherlands
# Devs:    Victor G.P. Reys, Shantanu Khatri
#===============================================================================
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh" # note: this also sets SCRIPT_DIR and REPO_ROOT

bash "$SCRIPT_DIR/01_python_env.sh"
bash "$SCRIPT_DIR/02_haddock_runner.sh"
bash "$SCRIPT_DIR/03_haddock3.sh"

for sys_dir in "$REPO_ROOT"/Docking_benchmarks/*/; do
  sys_dir="${sys_dir%/}"
  [ -f "$sys_dir/setup.sh" ] || continue
  sys="$(basename "$sys_dir")"
  log_file="$sys_dir/setup.log"
  echo "[+] Staging dataset for $sys"
  if (cd "$sys_dir" && bash setup.sh) >"$log_file" 2>&1; then
    echo "[+] $sys dataset staged"
  else
    echo "[!!] Staging $sys failed - see $log_file"
    exit 1
  fi
done

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------
source "$VENV_PATH/bin/activate"
echo
echo "==============================================================="
echo "  Setup complete"
echo "---------------------------------------------------------------"
echo "  haddock3        $(command -v haddock3)"
echo "  haddock-runner  $(command -v haddock-runner)"
echo "  python          $(python --version 2>&1)  ($VENV_PATH)"
echo "==============================================================="
echo
