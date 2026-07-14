# Usage

Assumes the environment is already set up via the `setup.sh` script.

## Run a scenario

```bash
./run.sh docking_benchmarks/<system>/<scenario>.yaml
```

Scenario YAMLs live directly under `docking_benchmarks/<system>/` (e.g. `protein_protein/HADDOCK3_clustfcc.yaml`). `run.sh` must be run from the repo root — it activates the venv and calls `binaries/haddock-runner` directly.

For long runs:

```bash
nohup ./run.sh <scenario.yaml> > run.out & disown && tail -f run.out
```

Without `run.sh`:

```bash
source .venv/bin/activate
export PATH="$PWD/binaries:$PATH"
haddock-runner docking_benchmarks/<system>/<scenario>.yaml
```

## SLURM defaults

`partition: short`, `ncores: 40`, `max_concurrent: 10` — edit directly in the scenario YAML to change.

## Analysing results

```bash
./analyse.sh <benchmark_results_dir>
```

Parses `capri_ss.tsv`, ranks by HADDOCK score, produces CAPRI plots + JSON summary. Full options in [analysis/README.md](analysis/README.md).

## Troubleshooting

- `Permission denied` on a setup script — `chmod +x setup.sh`
- `haddock-runner`/`haddock3` not found — use `run.sh`/`analyse.sh`, or manually: `source .venv/bin/activate && export PATH="$PWD/binaries:$PATH"`
- Wrong `work_dir` or missing input list — invoke from the repo root; scenario YAMLs use paths relative to themselves
- SLURM jobs fail immediately — check the partition exists (`sinfo`)
