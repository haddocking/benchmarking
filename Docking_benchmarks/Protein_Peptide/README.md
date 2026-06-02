# Protein-Peptide Docking Benchmarks

Benchmarking scenarios for protein-peptide docking using HADDOCK3. The peptide ligand is provided as a multi-model PDB ensemble; HADDOCK3 automatically detects MODEL records and treats it as an ensemble.

## Dataset

- Input list: `prot-peptide-input.txt`
- Molecule suffixes: `_r_u` (receptor, unbound), `_l_u` (peptide ligand, unbound ensemble)

## Scenarios

| Scenario | Description |
|---|---|
| `scenario_true_interface` | Docking using true interface restraints derived from the bound structure |
| `scenario_abinitio` | Ab initio docking without interface restraints |
| `scenario_clustfcc` | Docking with FCC-based clustering |

## Workflow

```
topoaa → rigidbody → caprieval → seletop → flexref → emref → clustrmsd → seletopclusts → caprieval
```

## SLURM settings

- `partition: short`
- `ncores: 40`
- `max_concurrent: 10`
