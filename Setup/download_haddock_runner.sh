
#!/bin/bash

set -euo pipefail

# ─────────────────────────────────────────────
#  haddock-runner  —  Setup Script
#
#  haddock-runner is the in-house orchestration
#  tool for large-scale HADDOCK docking scenarios.
#  It manages job submission, staging, and result
#  collection across cluster resources, and works
#  alongside Dirac, which handles job distribution
#  for HADDOCK web services.
#
#  This script installs the Rust toolchain (if
#  absent) and builds haddock-runner via Cargo.
# ─────────────────────────────────────────────

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

AUTO_YES=false

# ─── Argument parsing ────────────────────────

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

# ─── Helpers ─────────────────────────────────

banner() {
    echo ""
    echo -e "${BOLD}════════════════════════════════════════${RESET}"
    echo -e "${BOLD}  $1${RESET}"
    echo -e "${BOLD}════════════════════════════════════════${RESET}"
    echo ""
}

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

# ─── Load existing Cargo env ─────────────────

load_cargo_env() {
    if [ -f "$HOME/.cargo/env" ]; then
        # shellcheck source=/dev/null
        source "$HOME/.cargo/env"
    fi
}

load_cargo_env

# ─── Check existing Rust installation ────────

banner "haddock-runner  ·  Orchestrator Setup"

section "Checking Rust toolchain"

RUST_FOUND=false
CARGO_FOUND=false

command -v rustc &> /dev/null  && RUST_FOUND=true
command -v cargo &> /dev/null  && CARGO_FOUND=true

if [ "$RUST_FOUND" = true ];  then info "rustc:  $(rustc --version)";  else warn "rustc not found.";  fi
if [ "$CARGO_FOUND" = true ]; then info "cargo:  $(cargo --version)"; else warn "cargo not found."; fi

# ─── Install Rust if needed ──────────────────

if [ "$RUST_FOUND" = false ] || [ "$CARGO_FOUND" = false ]; then

    # Build a friendly list of what's missing
    missing=()
    [ "$RUST_FOUND"  = false ] && missing+=("Rust")
    [ "$CARGO_FOUND" = false ] && missing+=("Cargo")
    missing_str=$(IFS=" and "; echo "${missing[*]}")

    echo ""
    warn "${missing_str} not found."

    if confirm "Install Rust toolchain via rustup?"; then

        section "Installing Rust"

        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
            | sh -s -- -y --default-toolchain stable

        load_cargo_env

        info "Rust installed successfully."
        info "rustc:  $(rustc --version)"
        info "cargo:  $(cargo --version)"

    else
        error "Rust installation declined. haddock-runner is built with Cargo and cannot be installed without it."
        exit 1
    fi

else
    info "Rust and Cargo are already available."
fi

# ─── Ensure Cargo bin is in PATH (persistent) ─

section "Checking PATH configuration"

CARGO_BIN_LINE='export PATH="$HOME/.cargo/bin:$PATH"'
RC_UPDATED=false

for rc in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
    if [ -f "$rc" ] && ! grep -q 'cargo/bin' "$rc"; then
        echo "$CARGO_BIN_LINE" >> "$rc"
        info "Added Cargo to PATH in $rc"
        RC_UPDATED=true
    fi
done

# Also ensure it's active for this session
export PATH="$HOME/.cargo/bin:$PATH"

if [ "$RC_UPDATED" = false ]; then
    info "Cargo PATH already configured."
fi

# ─── Install haddock-runner ───────────────────
#
#  haddock-runner orchestrates large-scale docking
#  runs: it stages inputs, dispatches docking jobs,
#  and collects results. Dirac (a separate service)
#  handles the actual cluster job distribution for
#  HADDOCK web services and is not installed here.

section "Installing haddock-runner (orchestrator)"

RUNNER_BIN="$HOME/.cargo/bin/haddock-runner"
SKIP_INSTALL=false

if command -v haddock-runner &> /dev/null; then
    current_version="$(haddock-runner --version 2>/dev/null || echo "unknown")"
    info "haddock-runner is already installed: $current_version"

    if ! confirm "Reinstall / update haddock-runner?"; then
        SKIP_INSTALL=true
    fi
fi

if [ "$SKIP_INSTALL" = false ]; then
    echo ""
    echo "  Running: cargo install haddock-runner"
    echo ""
    cargo install haddock-runner
    info "haddock-runner installed successfully."
fi

# ─── Final verification ───────────────────────

banner "haddock-runner  ·  Ready"

if [ -x "$RUNNER_BIN" ] || command -v haddock-runner &> /dev/null; then
    info "Version:    $(haddock-runner --version)"
    info "Location:   $(command -v haddock-runner)"
else
    error "haddock-runner binary not found after install. Check cargo output above."
    exit 1
fi

echo ""
echo -e "  ${YELLOW}Note:${RESET} Restart your shell (or run ${BOLD}source ~/.bashrc${RESET}) to ensure PATH is current."
echo ""
echo -e "  haddock-runner is now ready to orchestrate large-scale docking scenarios."
echo -e "  For cluster job distribution via HADDOCK web services, ensure Dirac is"
echo -e "  configured and accessible on this host."
echo ""
