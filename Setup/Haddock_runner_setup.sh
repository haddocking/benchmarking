#!/usr/bin/env bash
#===============================================================================
# Setup: HADDOCK3 + haddock-runner (v3)
#
# Installs everything LOCALLY (no conda):
#   - pyenv + Python in $HOME/.pyenv
#   - a .venv virtualenv in the current directory
#   - HADDOCK3 (from PyPI) + matplotlib + rdkit into that venv
#   - haddock-runner v3 (Rust crate from crates.io) into $HOME/.cargo/bin
#===============================================================================
set -euo pipefail

PYTHON_VERSION=3.9.18   # Python version installed via pyenv
VENV_NAME=.venv         # virtualenv directory (created in the current folder)

# Pick the right shell rc so PATH edits land where YOUR shell will read them.
case "${SHELL:-}" in
  *zsh) PROFILE="$HOME/.zshrc"  ;;
  *)    PROFILE="$HOME/.bashrc" ;;
esac

# Append a line to $PROFILE only if it isn't already there.
add_to_profile() { grep -qsF "$1" "$PROFILE" 2>/dev/null || echo "$1" >> "$PROFILE"; }

#-------------------------------------------------------------------------------
# Python toolchain (pyenv, local, no conda)
#-------------------------------------------------------------------------------
# Install pyenv only if it isn't already present (gated on the dir, since the
# pyenv command may not be on PATH yet in a fresh shell).
if [ ! -d "$HOME/.pyenv" ]; then
  echo "[+] Installing pyenv"
  curl -fsSL https://pyenv.run | bash
fi
# Make pyenv load in future interactive shells (correct rc for your shell).
add_to_profile 'export PATH="$HOME/.pyenv/bin:$PATH"'
add_to_profile 'eval "$(pyenv init -)"'
add_to_profile 'eval "$(pyenv virtualenv-init -)"'

# Activate pyenv for THIS (non-interactive) shell.
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)" 2>/dev/null || true

# Install the target Python (-s = skip if already built) and select it.
echo "[+] Installing Python $PYTHON_VERSION (skipped if already built)"
pyenv install -s "$PYTHON_VERSION"
pyenv shell "$PYTHON_VERSION"

#-------------------------------------------------------------------------------
# Virtualenv
#-------------------------------------------------------------------------------
# Create the venv only if it doesn't exist, then activate it.
[ -d "$VENV_NAME" ] || python -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

#-------------------------------------------------------------------------------
# HADDOCK3 (+ workflow deps)
#-------------------------------------------------------------------------------
echo "[+] Installing HADDOCK3 from PyPI"
pip install haddock3
command -v haddock3 >/dev/null || { echo "[!!] HADDOCK3 install failed"; exit 1; }

echo "[+] Installing matplotlib + rdkit"
pip install matplotlib rdkit

#-------------------------------------------------------------------------------
# haddock-runner (v3 Rust crate; no prebuilt binary, so it must compile)
#-------------------------------------------------------------------------------
# Skip heavy LTO to keep the one-time compile fast.
export CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16

# Install a rustup-managed toolchain only if one isn't already present.
if [ ! -x "$HOME/.cargo/bin/cargo" ]; then
  echo "[+] Installing Rust toolchain"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --profile minimal --default-toolchain stable
fi
source "$HOME/.cargo/env"
export PATH="$HOME/.cargo/bin:$PATH"   # rustup cargo must win over any system v2
rustup update stable                   # haddock-runner 3.x needs rustc >=1.92 (edition 2024)

# Make ~/.cargo/bin available in future interactive shells too.
add_to_profile '. "$HOME/.cargo/env"'

echo "[+] Building haddock-runner"
cargo install --locked --force haddock-runner

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------
echo
echo "==============================================================="
echo "  Setup complete"
echo "---------------------------------------------------------------"
echo "  haddock3        $(command -v haddock3)"
echo "  haddock-runner  $(command -v haddock-runner)"
echo "  python          $(python --version 2>&1)  ($VENV_NAME)"
echo "==============================================================="
echo
echo "  Activate the Python env:"
echo "      source $VENV_NAME/bin/activate"
echo
echo "  If 'haddock-runner' is NOT found in a new shell, add this line to"
echo "  your shell's startup file, then open a new shell:"
echo
echo "      . \"\$HOME/.cargo/env\""
echo
