# Usage

This document describes how to run the HADDOCK benchmarking suite after the environment has been set up. For installation instructions, refer to [Setup/README.MD](../Setup/README.MD).

## Overview

The benchmarking suite uses [haddock-runner](https://github.com/haddocking/haddock-runner) to orchestrate large-scale docking runs across multiple targets and scenarios. Each scenario is defined by a YAML configuration file that specifies the input data, SLURM cluster settings, and the HADDOCK3 workflow to execute. The runner submits one SLURM job per target and manages concurrency automatically.

## Step 1 — Substitute absolute paths

All scenario YAML files use `_ABSPATH_PWD_` as a placeholder for the absolute path to this repository root. Before running any scenario, substitute the placeholder with the actual path:

```bash
find . -type f -name "*.yaml" -exec sed -i "s|_ABSPATH_PWD_|$PWD|g" {} +
```

This command must be run from the root of the repository. It modifies all scenario files in place.

## Step 2 — Run a scenario

To run a single benchmarking scenario:

```bash
./haddock-runner <path/to/scenario.yaml>
```

To run in the background and keep a persistent log (recommended for long benchmarks):

```bash
nohup ./haddock-runner <scenario.yaml> > run.out & disown && tail -f run.out
```

The `nohup` and `disown` ensure the process continues running if you disconnect from SSH. The output is streamed to `run.out` and you can monitor it live with `tail -f`.

## Scenario locations

Each benchmark type has its own directory under `Docking_benchmarks/`. See the README in each subdirectory for a description of what the scenarios test and how they differ.

| System | Scenario directory |
|---|---|
| Protein-Protein | [Docking_benchmarks/Protein_Protein/Scenarios/](../Docking_benchmarks/Protein_Protein/Scenarios/) |
| Protein-DNA | [Docking_benchmarks/Protein_DNA/Scenarios/](../Docking_benchmarks/Protein_DNA/Scenarios/) |
| Protein-Peptide | [Docking_benchmarks/Protein_Peptide/Scenarios/](../Docking_benchmarks/Protein_Peptide/Scenarios/) |
| Protein-Glycan | [Docking_benchmarks/Protein_Glycan/Scenarios/](../Docking_benchmarks/Protein_Glycan/Scenarios/) |
| Protein-Ligand Shape | [Docking_benchmarks/Protein_Ligand_Shape/Scenarios/](../Docking_benchmarks/Protein_Ligand_Shape/Scenarios/) |

## SLURM configuration

All scenarios are pre-configured to run on a SLURM cluster with the following defaults:

- `partition: short` — submits to the short partition queue
- `ncores: 40` — CPU cores requested per job
- `max_concurrent: 10` — limits the number of targets running at once to avoid overloading the queue

These settings can be modified directly in the scenario YAML file before running.

## Analysing results

Once a benchmark run has completed, use the analysis script to generate performance plots and summary statistics:

```bash
python Analysis/AnalyseBenchmarkResults.py <benchmark_results_dir>
```

The script parses the CAPRI evaluation output (`capri_ss.tsv`) from each target and scenario, ranks models by HADDOCK score, and produces stacked bar plots, violin plots, and a JSON performance summary. See [Analysis/README.md](../Analysis/README.md) for full documentation.

## Troubleshooting

- If `Permission denied` when running a setup script, make it executable first: `chmod +x setup.sh`
- If `haddock-runner: command not found`, run `source ~/.cargo/env` or open a new shell — the Cargo bin directory may not be on your PATH yet
- If `haddock3: command not found`, activate the virtual environment first: `source Setup/.venv/bin/activate`
- If paths are wrong in the YAML, re-run the `sed` substitution command from the repository root
- If SLURM jobs fail immediately, check the partition name matches what is available on your cluster (`sinfo` to list partitions)
