#!/usr/bin/env bash
#
# Sets up HADDOCK3 + haddock-runner. Everything goes in binaries/ and .venv,
# no conda, no changes to shell rc files.
#
# Runs scripts/01_python_env.sh, 02_haddock_runner.sh, 03_haddock3.sh, then
# stages every Docking_benchmarks/*/ dataset. Each step can also be run on
# its own, e.g. bash scripts/02_haddock_runner.sh to reinstall haddock-runner.
#
# Authors: BonvinLab, Computational Structural Biology group,
#          Utrecht University, the Netherlands
# Devs:    Victor G.P. Reys, Shantanu Khatri
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$THIS_DIR/scripts/_common.sh"

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

# Summary
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
