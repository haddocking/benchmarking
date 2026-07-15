#!/usr/bin/env bash
#
# Python + venv setup, no conda.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

if [ ! -x "$BIN_DIR/uv" ]; then
  echo "[+] Installing uv into $BIN_DIR"
  curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="$BIN_DIR" sh
fi

echo "[+] Creating venv with Python $PYTHON_VERSION"
[ -d "$VENV_PATH" ] || uv venv --python "$PYTHON_VERSION" "$VENV_PATH"
