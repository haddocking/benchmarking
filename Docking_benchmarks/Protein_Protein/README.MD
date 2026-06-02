# Protein-Protein Docking Benchmarks

Benchmarking scenarios for protein-protein docking using the BM5 dataset with HADDOCK2.4 and HADDOCK3.

## Dataset

- Input list: `bm5-input.txt`
- Molecule suffixes: `_r_u` (receptor, unbound), `_l_u` (ligand, unbound)

## Scenarios

| Scenario | Tool | Description |
|---|---|---|
| `scenario_HADDOCK24_default` | HADDOCK2.4 | Default protocol: rigidbody → flexref → mdref, clustered by FCC |
| `scenario_HADDOCK24_default_5Aambig` | HADDOCK2.4 | Default protocol with 5 Å ambiguous distance restraints |
| `scenario_HADDOCK24_ab_initio` | HADDOCK2.4 | Ab initio docking without restraints |
| `scenario_HADDOCK3_clustfcc` | HADDOCK3 | HADDOCK3 pipeline clustered by FCC |
| `scenario_HADDOCK3_ilrmsdclustering` | HADDOCK3 | HADDOCK3 pipeline clustered by interface-ligand RMSD |

## Workflow (default)

```
topoaa → rigidbody → caprieval → seletop → flexref → mdref → clustfcc/clustrmsd → seletopclusts → caprieval
```

## SLURM settings

- `partition: short`
- `ncores: 40`
- `max_concurrent: 10`
