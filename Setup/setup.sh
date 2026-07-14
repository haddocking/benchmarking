#!/usr/bin/env bash
#===============================================================================
# Setup: HADDOCK3 + haddock-runner (v3)
#
# Orchestrates three independent steps (installs everything LOCALLY, no conda).
# uv and haddock-runner are placed in <repo>/binaries/, not ~/.local/bin, so
# every checkout of this repo carries its own pinned copies:
#   1. scripts/01_python_env.sh      - uv (in binaries/) + Python 3.14 + .venv
#   2. scripts/02_haddock_runner.sh  - haddock-runner (prebuilt binary, in binaries/)
#   3. scripts/03_haddock3.sh        - HADDOCK3 + matplotlib + rdkit into .venv
#
# Each step is idempotent and can also be run standalone, e.g. to reinstall
# just haddock-runner: bash Setup/scripts/02_haddock_runner.sh
#
# Authors: BonvinLab, Computational Structural Biology group,
#          Utrecht University, the Netherlands
# Devs:    Victor G.P. Reys, Shantanu Khatri
#===============================================================================
set -euo pipefail

SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SETUP_DIR/scripts/_common.sh" # note: this also sets SCRIPT_DIR

bash "$SCRIPT_DIR/01_python_env.sh"
bash "$SCRIPT_DIR/02_haddock_runner.sh"
bash "$SCRIPT_DIR/03_haddock3.sh"

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
