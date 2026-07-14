#!/usr/bin/env bash
#===============================================================================
# Shared paths and helpers sourced by every scripts/*.sh step.
#===============================================================================
set -euo pipefail

PYTHON_VERSION=3.14 # Python version installed/managed by uv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" # repo_root/scripts
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$REPO_ROOT/.venv"
BIN_DIR="$REPO_ROOT/binaries" # uv + haddock-runner live here

mkdir -p "$BIN_DIR"

# Make locally-installed tools (uv, haddock-runner) visible in this process.
export PATH="$BIN_DIR:$PATH"
