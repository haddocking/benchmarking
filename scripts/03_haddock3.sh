#!/usr/bin/env bash
#===============================================================================
# Step 3: HADDOCK3 + workflow deps into the venv created by 01_python_env.sh
#===============================================================================
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

echo "[+] Installing HADDOCK3"
uv pip install --python "$VENV_PATH/bin/python" haddock3
[ -x "$VENV_PATH/bin/haddock3" ] || {
  echo "[!!] HADDOCK3 install failed"
  exit 1
}

echo "[+] Installing matplotlib + rdkit"
uv pip install --python "$VENV_PATH/bin/python" matplotlib rdkit
