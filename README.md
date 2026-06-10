<p align="center">
  <img src="images/banner_1200dpi.png" width="100%" style="display:block; margin:0; padding:0;"/>
</p>

# HADDOCK Benchmarking Suite

[HADDOCK3](https://github.com/haddocking/haddock3) is an information-driven docking platform developed at BonvinLab, Utrecht University, that uses experimental or predicted binding-site data as ambiguous interaction restraints to guide the assembly of biomolecular complexes. Benchmarking evaluates how reliably a docking protocol can predict the correct bound structure when starting only from the free, unbound partners — by running hundreds of complexes with known crystal structures and scoring the results against CAPRI quality thresholds (High / Medium / Acceptable). This repository provides the datasets, scenario YAML files, setup scripts, and analysis pipeline to run and compare those benchmarks across five molecular system types: protein-protein, protein-peptide, protein-DNA, protein-glycan, and shape-guided protein-ligand docking. All benchmarks are orchestrated by [haddock-runner](https://github.com/haddocking/haddock-runner), an in-house Rust tool that reads scenario YAML files, stages inputs, and dispatches SLURM jobs across cluster nodes.

## Repository Structure

```
Benchmarking/
├── Setup/                      # Environment setup scripts → Setup/README.MD
├── Docking_benchmarks/
│   ├── Protein_Protein/        # BM5 protein-protein benchmark (230 complexes)
│   ├── Protein_Peptide/        # Protein-peptide benchmark
│   ├── Protein_DNA/            # Protein-DNA benchmark
│   ├── Protein_Glycan/         # Protein-glycan benchmark
│   └── Protein_Ligand_Shape/   # Shape-guided protein-ligand benchmark
├── Analysis/                   # Post-run analysis and visualisation → Analysis/README.md
└── Usage/                      # Full usage guide → Usage/README.MD
```

Each benchmark directory follows the same layout (shown for `Protein_Protein/`):

```
Protein_Protein/
├── README.MD                               # Dataset description, scenarios, and run instructions
├── setup.sh                                # Downloads and stages input structures
└── Scenarios/                              # YAML scenario files — one per docking protocol
    ├── scenario_HADDOCK24_default.yaml
    ├── scenario_HADDOCK24_default_5Aambig.yaml
    ├── scenario_HADDOCK24_ab_initio.yaml
    ├── scenario_HADDOCK3_clustfcc.yaml
    └── scenario_HADDOCK3_ilrmsdclustering.yaml
```

## Quick Start

**1. Set up the environment**

Run the setup script from the repository root. It installs pyenv, Python 3.9.18, a local virtual environment, HADDOCK3, and haddock-runner — nothing is changed system-wide.

```bash
bash Setup/Haddock_runner_setup.sh
```

See [Setup/README.MD](Setup/README.MD) for prerequisites, a step-by-step description of what the script does, and troubleshooting notes.

**2. Substitute absolute paths in scenario files**

Run this once from the repository root before running any benchmark:

```bash
find . -type f -name "*.yaml" -exec sed -i "s|_ABSPATH_PWD_|$PWD|g" {} +
```

**3. Run a benchmark scenario**

```bash
./haddock-runner Docking_benchmarks/Protein_Protein/Scenarios/scenario_HADDOCK3_clustfcc.yaml
```

For long runs, use `nohup` and `disown` to keep the job alive after disconnecting from SSH:

```bash
nohup ./haddock-runner <scenario.yaml> > run.out & disown && tail -f run.out
```

See [Usage/README.MD](Usage/README.MD) for the full guide including SLURM configuration and troubleshooting.

## Pipeline Overview

<p align="center">
  <img src="images/haddock_runner_sequence_compact_v2.svg" width="75%" style="display:block; margin:0; padding:0;"/>
</p>

## Benchmark Systems

| System | Dataset | Scenarios | Documentation |
|---|---|---|---|
| Protein-Protein | BM5 (230 complexes) | 5 | [Docking_benchmarks/Protein_Protein/](Docking_benchmarks/Protein_Protein/) |
| Protein-Peptide | – | 3 | [Docking_benchmarks/Protein_Peptide/](Docking_benchmarks/Protein_Peptide/) |
| Protein-DNA | – | 3 | [Docking_benchmarks/Protein_DNA/](Docking_benchmarks/Protein_DNA/) |
| Protein-Glycan | – | 3 | [Docking_benchmarks/Protein_Glycan/](Docking_benchmarks/Protein_Glycan/) |
| Protein-Ligand Shape | – | 2 | [Docking_benchmarks/Protein_Ligand_Shape/](Docking_benchmarks/Protein_Ligand_Shape/) |

Each subdirectory README describes the biological context, input dataset, restraint strategy, the HADDOCK3 workflow for each scenario, and the exact run command.

### Scenario overview

**Protein-Protein (BM5)** — evaluates five protocols ranging from fully restrained docking (default HADDOCK2.4 AIRs) to completely blind ab initio docking, plus two HADDOCK3-specific early-clustering protocols (FCC and ilRMSD-based).

**Protein-Peptide** — benchmarks three strategies: best-case true-interface restraints, fully blind ab initio docking (10,000 rigid-body models), and an early FCC clustering protocol.

**Protein-DNA** — tests docking across three difficulty levels (bound-bound, bound-unbound, unbound-unbound) with DNA-specific force field parameters to handle the polyanionic backbone.

**Protein-Glycan** — uses topological interaction (TI) restraints to guide docking of inherently flexible glycan chains; scenarios cover bound and unbound conformations and ensemble-based glycan sampling.

**Protein-Ligand Shape** — evaluates shape-bead-guided docking and pharmacophore-enhanced shape docking for cases where only approximate ligand geometry is available.

## Analysis

After a benchmark run completes, generate CAPRI performance plots and a JSON summary:

```bash
python3 Analysis/AnalyseBenchmarkResults.py <benchmark_results_dir> -t protein -m irmsd
```

The script classifies docking models by CAPRI quality (High / Medium / Acceptable / Near-acceptable / Low) at Top1–Top1000 thresholds and produces stacked bar plots, violin plots, melquiplots, and a JSON performance report. See [Analysis/README.md](Analysis/README.md) for the full option reference and output file descriptions.

## Contributing

See [contributing.md](contributing.md) for instructions on adding new scenarios, new benchmark systems, or improvements to the analysis pipeline.

## License

[Apache License 2.0](LICENSE)
