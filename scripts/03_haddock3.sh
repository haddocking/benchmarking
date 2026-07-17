#!/usr/bin/env bash
#
# HADDOCK3 + workflow deps into the venv from 01_python_env.sh.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

# Check if the version is from pypi or a commit
if [[ "$HADDOCK3_VERSION" =~ ^[0-9a-fA-F]{7,40}$ ]]; then
  echo "[+] Installing HADDOCK3 from commit $HADDOCK3_VERSION"
  CMD="haddock3 @ git+https://github.com/haddocking/haddock3.git@$HADDOCK3_VERSION"
else
  echo "[+] Installing HADDOCK3 $HADDOCK3_VERSION from pypi"
  CMD="haddock3==$HADDOCK3_VERSION"
fi

uv pip install --python "$VENV_PATH/bin/python" "$CMD"
[ -x "$VENV_PATH/bin/haddock3" ] || {
  echo "[!!] HADDOCK3 install failed"
  exit 1
}

echo "[+] Installing matplotlib + rdkit"
uv pip install --python "$VENV_PATH/bin/python" matplotlib rdkit
