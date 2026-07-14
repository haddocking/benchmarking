#!/usr/bin/env bash
#
# Shared paths, sourced by every scripts/*.sh step.
set -euo pipefail

PYTHON_VERSION=3.14

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$REPO_ROOT/.venv"
BIN_DIR="$REPO_ROOT/binaries"

mkdir -p "$BIN_DIR"
export PATH="$BIN_DIR:$PATH"
