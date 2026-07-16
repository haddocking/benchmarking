#!/usr/bin/env bash
#
# HADDOCK3 + workflow deps into the venv from 01_python_env.sh.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

echo "[+] Installing HADDOCK3 $HADDOCK3_VERSION"
uv pip install --python "$VENV_PATH/bin/python" "haddock3==$HADDOCK3_VERSION"
[ -x "$VENV_PATH/bin/haddock3" ] || {
  echo "[!!] HADDOCK3 install failed"
  exit 1
}

echo "[+] Installing matplotlib + rdkit"
uv pip install --python "$VENV_PATH/bin/python" matplotlib rdkit
