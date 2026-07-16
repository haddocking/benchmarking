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

source "$REPO_ROOT/versions.env"

# helper function to clone a specific commit
clone_pinned() {
  # clone_pinned <url> <dir> <ref>
  local url="$1" dir="$2" ref="$3"
  if [ -d "$dir" ] && [ ! -d "$dir/.git" ]; then
    # pre-pin layout: dataset was cloned without keeping .git, can't be fetched/checked
    # out in place. It's a regenerable download (see .gitignore), so wipe and re-clone.
    echo "[!] $dir has no .git (pre-pin layout) - re-cloning to pin $ref"
    rm -rf "$dir"
  fi
  if [ ! -d "$dir/.git" ]; then
    git clone "$url" "$dir"
  fi
  git -C "$dir" fetch --quiet origin "$ref" || git -C "$dir" fetch --quiet --tags origin
  git -C "$dir" checkout --quiet "$ref"
}
