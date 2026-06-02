# Protein-Glycan Docking Benchmarks

Benchmarking scenarios for protein-glycan docking using HADDOCK3 with van der Waals and topological interaction restraints.

## Dataset

- Input list: `prot-glycan-input.txt`
- Molecule suffixes: `_r_b` (receptor, bound), `_l_b` (ligand/glycan, bound) or unbound variants

## Scenarios

| Scenario | Description |
|---|---|
| `scenario1_bound_vdw_ti-aa` | Bound-bound docking with VdW energy term and topological interaction restraints (ti-aa) |
| `scenario2_unbound_vdw_tip_ap` | Unbound docking with VdW + topological interaction point restraints (tip-ap) |
| `scenario3_unbound_ens_vdw_tipap_clust` | Unbound ensemble docking with VdW + tip-ap restraints and RMSD clustering |

## Workflow

```
topoaa → rigidbody → caprieval → ilrmsdmatrix → clustrmsd → seletopclusts → flexref → caprieval → clustrmsd → seletopclusts → caprieval
```

## Notes

- `keep_hetatm: true` is set in caprieval steps to retain glycan HETATM records during evaluation
- Clustering uses both `maxclust` (top 50 clusters) and distance-based cutoff (2.5 Å) strategies

## SLURM settings

- `partition: short`
- `ncores: 40`
- `max_concurrent: 10`
