# Analysis

This directory contains the post-processing and visualisation script for HADDOCK benchmarking results produced by `haddock-runner`.

## Two levels of analysis

**Per-run analysis (automatic)** — HADDOCK automatically generates an `analysis/` folder inside each target's `run1/` directory as part of the docking workflow. This contains per-target HTML reports (`report.html`), scatter plots, and a `capri_ss.tsv` evaluation file. It is created by the `caprieval` module and requires no manual step.

**Benchmark-wide analysis (manual)** — once all targets across a scenario have finished, `AnalyseBenchmarkResults.py` aggregates the `capri_ss.tsv` files from every target and produces overall performance plots and a JSON summary across the full dataset. This is what you run manually after the benchmark completes.

## Script

### `AnalyseBenchmarkResults.py`

**Version**: 1.1.1  
**Author**: BonvinLab, Computational Structural Biology group, Utrecht University

The script reads `capri_ss.tsv` files produced by the `caprieval` module of HADDOCK3, ranks models by their HADDOCK score, and computes the quality of the best-ranking model at a series of top-X thresholds (Top1, Top5, Top10, Top20, Top50, Top100, Top200, Top500, Top1000). Results are classified into CAPRI performance categories and visualised across all scenarios and pipeline stages.

## Requirements

```bash
pip install numpy matplotlib
```

Both packages are already installed if you ran `Setup/Haddock_runner_setup.sh`.

## Expected Input Structure

The script expects a benchmark results directory in the format produced by `haddock-runner`. Each target is a subdirectory named by its PDB ID, and within each target there is one subdirectory per scenario, each containing a `run1/` directory with the HADDOCK3 output.

```
<benchmark_results_dir>/
  <PDBid>/
    <scenario_name>/
      run1/
        02_caprieval/
          capri_ss.tsv
        04_caprieval/
          capri_ss.tsv
        06_caprieval/
          capri_ss.tsv
        ...
```

If HADDOCK3 was run with `gen_archive = true`, the analysis can be read directly from the compressed analysis archives (`run1_analysis.tgz`) using the `--from-archive` flag.

## Basic Usage

```bash
python3 Analysis/AnalyseBenchmarkResults.py <path/to/benchmark_results_dir/>
```

Output files are written to an `Analysis/` subdirectory by default.

## All Options

```
positional arguments:
  benchmark_directory     Path to the directory where the benchmark was run

optional arguments:
  -o, --output_path       Directory to write output files (default: Analysis/)
  -m, --metric            Performance metric: irmsd or dockq (default: irmsd)
  -s, --scenario          Analyse only specific scenario(s) by name (default: all)
  -t, --type              System type for CAPRI thresholds: protein, peptide, glycan (default: protein)
  -d, --dpi               DPI for output figures (default: 400)
  -n, --no-percentage     Report raw counts instead of percentages in bar plots
  -a, --from-archive      Read capri_ss.tsv from run1_analysis.tgz archives
  -q, --quiet             Suppress all stdout output
  --no-capriplots         Skip CAPRI bar plot generation
  --no-violinplots        Skip violin plot generation
  --no-melquiplots        Skip melquiplot generation
```

## Output Files

Running the script produces the following files in the output directory:

| File | Description |
|---|---|
| `*_performances.json` | JSON summary of best model quality at each top-X threshold per scenario and caprieval stage |
| `*_capribarpolots.png` | Stacked bar plots showing the fraction of targets with High / Medium / Acceptable / Near-acceptable / Low quality models at each threshold, for each scenario and caprieval stage |
| `*_violins.png` | Violin plots showing the distribution of performance metric values across all targets, broken down by scenario and caprieval stage |
| `*_melquiplots.zip` | Archive of per-scenario melquiplots — one column per target, one row per caprieval stage, colour-coded by CAPRI quality class |
| `*_benchmark_mapper.json` | Internal mapping of scenario/target/stage to file paths (cached to speed up re-runs) |

## Performance Classes

Models are classified according to CAPRI criteria. The thresholds differ by system type and metric:

**Protein-Protein / Protein-DNA (iRMSD)**

| Class | iRMSD range |
|---|---|
| High | < 1 Å |
| Medium | 1 – 2 Å |
| Acceptable | 2 – 4 Å |
| Near-acceptable | 4 – 6 Å |
| Low | > 6 Å |
| Missing | No model generated |

**Protein-Peptide / Protein-Glycan (iRMSD)**

| Class | iRMSD range |
|---|---|
| High | < 0.5 Å |
| Medium | 0.5 – 1 Å |
| Acceptable | 1 – 2 Å |
| Near-acceptable | 2 – 3 Å |
| Low | > 3 Å |

DockQ thresholds are also available (`--metric dockq`) with corresponding class boundaries defined in the script.

## Customising Caprieval Stage Labels

By default, caprieval stages are labelled by their module index (e.g. `02`, `04`). You can assign human-readable names by editing the `CAPRIEVAL_STEPS` dictionary near the top of the script:

```python
CAPRIEVAL_STEPS = {
    '02': 'rigidbody',
    '04': 'seletop 200',
    '06': 'flexref',
    '08': 'emref',
    '11': 'top 4 models per fcc clust',
}
```

The keys must match the two-digit index prefix of the caprieval directories in the HADDOCK3 run output (e.g. `02_caprieval/`). Any stage not listed here will be labelled `<index>_caprieval` automatically.

## Examples

Analyse all scenarios for a protein-protein benchmark run:

```bash
python3 Analysis/AnalyseBenchmarkResults.py results/protein-protein/ -t protein -m irmsd
```

Analyse only two specific scenarios and suppress plots:

```bash
python3 Analysis/AnalyseBenchmarkResults.py results/protein-protein/ \
    -s scenario-HADDOCK3_clustfcc scenario-HADDOCK3_ilrmsdclustering \
    --no-melquiplots
```

Read results from compressed archives (when `gen_archive = true` was set in HADDOCK3):

```bash
python3 Analysis/AnalyseBenchmarkResults.py results/protein-peptide/ -t peptide -a
```
