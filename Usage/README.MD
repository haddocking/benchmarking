# Usage

Instructions for running the HADDOCK benchmarking suite after setup is complete.

## Prerequisites

Run the setup script first (see `Setup/README.MD`):

```bash
bash Setup/Haddock_runner_setup.sh
```

## Replacing paths

All scenario files use `_ABSPATH_PWD_` as a placeholder for the absolute path to this directory. Before running, substitute it with the actual path:

```bash
find . -type f -name "*.yaml" -exec sed -i "s|_ABSPATH_PWD_|$PWD|g" {} +
```

## Running a scenario

```bash
./haddock-runner <path/to/scenario.yaml>
```

To run in the background and keep output:

```bash
nohup ./haddock-runner <scenario.yaml> > run.out & disown && tail -f run.out
```

## Scenario locations

| System | Scenarios |
|---|---|
| Protein-Protein | `Docking_benchmarks/Protein_Protein/Scenarios/` |
| Protein-DNA | `Docking_benchmarks/Protein_DNA/scenarios/` |
| Protein-Peptide | `Docking_benchmarks/Protein_Peptide/Scenarios/` |
| Protein-Glycan | `Docking_benchmarks/Protein_Glycan/scenarios/` |
| Protein-Ligand Shape | `Docking_benchmarks/Protein_Ligand_Shape/scenario/` |

## Analysing results

After a run completes, use the analysis script:

```bash
python Analysis/AnalyseBenchmarkResults.py <benchmark_results_dir>
```

See `Analysis/README.md` for full documentation.
