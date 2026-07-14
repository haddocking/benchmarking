#!/usr/bin/env bash
#===============================================================================
# Step 1: Python toolchain + virtualenv (uv, local, no conda)
#===============================================================================
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

# Install uv straight into the repo's binaries/ dir (skipped if already there).
if [ ! -x "$BIN_DIR/uv" ]; then
  echo "[+] Installing uv into $BIN_DIR"
  curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="$BIN_DIR" sh
fi

# uv fetches the target Python version on demand and builds the venv in one
# step (skipped if the venv already exists).
echo "[+] Creating venv with Python $PYTHON_VERSION"
[ -d "$VENV_PATH" ] || uv venv --python "$PYTHON_VERSION" "$VENV_PATH"
