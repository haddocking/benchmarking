#!/bin/bash

set -euo pipefail

#===============================================================================
#  Setup script — installs Python environment, HADDOCK3, and haddock-runner
#===============================================================================

export PYTHON_VERSION=3.9.18
export VENV_NAME=.venv

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

AUTO_YES=false

# ─── Argument parsing ────────────────────────────────────────────────────────

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes     Non-interactive mode (auto-confirm all prompts)"
    echo "  -h, --help    Show this help message"
    exit 0
}

for arg in "$@"; do
    case "$arg" in
        -y|--yes)  AUTO_YES=true ;;
        -h|--help) usage ;;
        *)
            echo -e "${RED}Unknown argument: $arg${RESET}"
            usage
            ;;
    esac
done

# ─── Helpers ─────────────────────────────────────────────────────────────────

info()    { echo -e "  ${GREEN}✔${RESET}  $1"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
error()   { echo -e "  ${RED}✘${RESET}  $1"; }
section() { echo -e "\n${BOLD}▸ $1${RESET}"; }

confirm() {
    local prompt="$1"
    if [ "$AUTO_YES" = true ]; then
        echo "  (auto-yes) $prompt → y"
        return 0
    fi
    read -rp "  $prompt (y/n): " choice
    [[ "$choice" =~ ^[Yy]$ ]]
}

trap 'error "Setup failed at line $LINENO. Exiting."; exit 1' ERR

# ─── Confirmation ─────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}════════════════════════════════════════${RESET}"
echo -e "${BOLD}  HADDOCK Benchmarking Suite — Setup${RESET}"
echo -e "${BOLD}════════════════════════════════════════${RESET}"
echo ""
echo "  This script will install:"
echo "    - pyenv + Python ${PYTHON_VERSION} (in \$HOME/.pyenv)"
echo "    - a virtual environment (${VENV_NAME}) in the current directory"
echo "    - HADDOCK3, matplotlib, rdkit"
echo "    - Rust toolchain (if absent)"
echo "    - haddock-runner (via cargo)"
echo ""
echo -e "  ${YELLOW}Note:${RESET} This does NOT use Anaconda/Miniconda."
echo ""

if ! confirm "Do you want to continue?"; then
    echo "  Exiting."
    exit 1
fi

# ─── Python / pyenv ──────────────────────────────────────────────────────────

section "Checking pyenv"

if ! command -v pyenv &> /dev/null; then
    warn "pyenv not found — installing"
    curl https://pyenv.run | bash
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
fi

# Load pyenv into the current script session directly
# (source ~/.bashrc does not work in non-interactive scripts)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

if ! pyenv versions | grep "${PYTHON_VERSION}" &> /dev/null; then
    section "Installing Python ${PYTHON_VERSION}"
    pyenv install "${PYTHON_VERSION}"
fi

info "Activating Python ${PYTHON_VERSION}"
pyenv shell "${PYTHON_VERSION}"

# ─── Virtual environment ──────────────────────────────────────────────────────

section "Virtual environment"

if [ ! -d "${VENV_NAME}" ]; then
    info "Creating virtual environment"
    python -m venv "${VENV_NAME}"
fi

source "${VENV_NAME}/bin/activate"
info "Virtual environment active"

# ─── HADDOCK3 ────────────────────────────────────────────────────────────────

section "HADDOCK3"

info "Installing haddock3, matplotlib, and rdkit"
pip install haddock3 matplotlib rdkit

if ! command -v haddock3 &> /dev/null; then
    error "haddock3 could not be found after install — check the output above"
    exit 1
fi

# ─── Rust toolchain ──────────────────────────────────────────────────────────

section "Checking Rust toolchain"

load_cargo_env() {
    [ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"
}

load_cargo_env

RUST_FOUND=false
CARGO_FOUND=false
command -v rustc &> /dev/null && RUST_FOUND=true
command -v cargo &> /dev/null && CARGO_FOUND=true

if [ "$RUST_FOUND" = true ];  then info "rustc:  $(rustc --version)";  else warn "rustc not found";  fi
if [ "$CARGO_FOUND" = true ]; then info "cargo:  $(cargo --version)"; else warn "cargo not found"; fi

if [ "$RUST_FOUND" = false ] || [ "$CARGO_FOUND" = false ]; then
    if confirm "Install Rust toolchain via rustup?"; then
        section "Installing Rust"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
            | sh -s -- -y --default-toolchain stable
        load_cargo_env
        info "Rust installed: $(rustc --version)"
    else
        error "Rust installation declined — haddock-runner requires Cargo"
        exit 1
    fi
else
    info "Rust and Cargo already available"
fi

# Ensure cargo bin is in PATH
CARGO_BIN_LINE='export PATH="$HOME/.cargo/bin:$PATH"'
for rc in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
    if [ -f "$rc" ] && ! grep -q 'cargo/bin' "$rc"; then
        echo "$CARGO_BIN_LINE" >> "$rc"
        info "Added Cargo to PATH in $rc"
    fi
done
export PATH="$HOME/.cargo/bin:$PATH"

# ─── haddock-runner ──────────────────────────────────────────────────────────

section "Installing haddock-runner"

SKIP_INSTALL=false
if command -v haddock-runner &> /dev/null; then
    info "haddock-runner already installed: $(haddock-runner --version 2>/dev/null || echo unknown)"
    if ! confirm "Reinstall / update haddock-runner?"; then
        SKIP_INSTALL=true
    fi
fi

if [ "$SKIP_INSTALL" = false ]; then
    cargo install haddock-runner
    info "haddock-runner installed successfully"
fi

# ─── Done ────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}════════════════════════════════════════${RESET}"
echo -e "${BOLD}  Setup complete${RESET}"
echo -e "${BOLD}════════════════════════════════════════${RESET}"
echo ""
info "haddock-runner: $(haddock-runner --version)"
info "Location:       $(command -v haddock-runner)"
echo ""
echo -e "  ${YELLOW}Note:${RESET} Restart your shell (or run ${BOLD}source ~/.bashrc${RESET}) to ensure PATH is current."
echo ""
