# Setup

This directory contains the setup script for the HADDOCK benchmarking environment. Everything is installed locally — nothing is installed system-wide. All software lands in your home directory (`~/.pyenv`, `~/.cargo`) or in the repository's `.venv`.

## What gets installed

| Component | How | Location |
|---|---|---|
| Python 3.9.18 | pyenv | `~/.pyenv` |
| Virtual environment | `python -m venv` | `.venv/` in repo root |
| HADDOCK3 | `pip install haddock3` (PyPI) | `.venv/` |
| matplotlib + rdkit | pip | `.venv/` |
| Rust toolchain | rustup | `~/.cargo` |
| haddock-runner | `cargo install` (crates.io) | `~/.cargo/bin` |

## Prerequisites

- `bash` or `zsh`
- `curl`
- Internet connection (pyenv, Python, HADDOCK3, Rust, and haddock-runner are all downloaded)
- A SLURM-managed cluster (required for running benchmarks; setup itself does not need SLURM)

## Running the setup

From the root of the repository:

```bash
bash Setup/Haddock_runner_setup.sh
```

The script detects your shell (zsh or bash) and writes PATH updates to the correct rc file (`~/.zshrc` or `~/.bashrc`). Steps are skipped automatically if the component is already present.

After setup completes, open a new shell (or `source ~/.zshrc` / `source ~/.bashrc`) to ensure `haddock-runner` is on your PATH.

## Notes

- **No conda** — Python is managed entirely through pyenv to avoid conflicts on shared cluster environments.
- **Re-running is safe** — each step checks for existing installations and skips if already done (`pyenv install -s`, venv directory check, cargo binary check).
- **HADDOCK3 is installed from PyPI** — no source clone needed. To upgrade: `pip install --upgrade haddock3` inside the activated venv.
- **haddock-runner compiles from source** — the first install takes a few minutes while Cargo builds the binary. LTO is disabled to keep compile time short.
