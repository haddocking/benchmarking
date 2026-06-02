# Setup

This directory contains all the scripts needed to set up the HADDOCK benchmarking environment on a cluster. The setup is entirely local — nothing is installed system-wide and no changes are made for other users. All software is installed inside the repository directory or under your home directory (`~/.pyenv`, `~/.cargo`).

## Overview

The benchmarking suite depends on two main components:

- **HADDOCK3** — the docking engine, installed inside a local Python virtual environment
- **haddock-runner** — the orchestration tool that reads scenario YAML files, stages inputs, and dispatches SLURM jobs across cluster nodes

Both are installed by the scripts in this directory.

## Files

| File | Description |
|---|---|
| `Haddock_runner_setup.sh` | Main setup script — installs pyenv, Python 3.9.18, a virtual environment, HADDOCK3, and downloads haddock-runner |
| `download_haddock_runner.sh` | Installs the Rust toolchain (if absent) and builds haddock-runner via Cargo |
| `run-haddock3.sh` | Thin wrapper script that activates the virtual environment and calls `haddock3` — used internally by haddock-runner to invoke HADDOCK3 jobs |

## Prerequisites

The following must be available on the system before running setup:

- `bash` (4.0+)
- `curl`
- `git`
- A working internet connection (for downloading pyenv, Python, HADDOCK3, Rust, and haddock-runner)
- A SLURM-managed cluster (required for running benchmarks; setup itself does not need SLURM)

## Running the Setup

From the root of the repository, run:

```bash
bash Setup/Haddock_runner_setup.sh
```

The script will prompt for confirmation before proceeding. It performs the following steps in order:

1. **Install pyenv** — clones pyenv into `~/.pyenv` and adds the necessary initialisation lines to `~/.bashrc` if not already present
2. **Install Python 3.9.18** — compiles Python 3.9.18 via pyenv and sets it as the active version for the current shell
3. **Create virtual environment** — creates a `.venv` directory in the repository root using the pyenv-managed Python
4. **Clone and install HADDOCK3** — clones the HADDOCK3 repository and installs it in development mode into the virtual environment using `pip install .`
5. **Install dependencies** — installs `matplotlib` and `rdkit` into the virtual environment
6. **Download haddock-runner** — runs `download_haddock_runner.sh` to install the Rust toolchain and build haddock-runner

After setup completes, substitute the `_ABSPATH_PWD_` placeholder in all scenario files before running any benchmark:

```bash
find . -type f -name "*.yaml" -exec sed -i "s|_ABSPATH_PWD_|$PWD|g" {} +
```

## haddock-runner Installation (`download_haddock_runner.sh`)

This script installs `haddock-runner`, the in-house orchestration tool for large-scale docking scenarios. It manages SLURM job submission, input staging, and result collection based on the scenario YAML files. It is written in Rust and installed via Cargo.

The script:

1. Checks whether `rustc` and `cargo` are already available
2. If not, downloads and installs the Rust toolchain via `rustup` (installed to `~/.cargo`)
3. Adds `~/.cargo/bin` to `PATH` in `~/.bashrc`, `~/.bash_profile`, and `~/.profile` if not already present
4. Runs `cargo install haddock-runner` to download, compile, and install the binary

To run non-interactively (e.g. in a batch job or CI):

```bash
bash Setup/download_haddock_runner.sh --yes
```

After installation, restart your shell or run `source ~/.bashrc` to ensure the `haddock-runner` binary is on your `PATH`.

## run-haddock3.sh

This is a thin wrapper around the `haddock3` command. It activates the local virtual environment and passes all arguments through to HADDOCK3. It is called internally by `haddock-runner` to execute each docking job and should not need to be invoked manually.

The `_ABSPATH_PWD_` placeholder in this file is replaced with the actual repository path by the setup script (`sed -i "s|_ABSPATH_PWD_|$PWD|g" run-haddock3.sh`).

## Important Notes

- **Do not use Anaconda or Miniconda** — the setup explicitly avoids conda environments to prevent conflicts with other users on the cluster. All Python management is done through pyenv.
- **Local installation only** — pyenv, the virtual environment, and all installed packages are contained within your home directory and this repository. Uninstalling is as simple as deleting `.venv/`, `haddock3/`, and `~/.pyenv/`.
- **HADDOCK3 is installed in editable mode** — changes to the `haddock3/` source tree will be reflected immediately without reinstalling.
- **Re-running the setup script is safe** — it checks for existing installations at each step and skips steps that have already been completed.
