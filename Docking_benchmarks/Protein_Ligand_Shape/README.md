# Protein-Ligand Shape Docking Benchmarks

Benchmarking scenarios for protein-ligand docking guided by ligand shape information using HADDOCK3. Shape beads derived from the ligand are used as a surrogate to guide docking in the absence of exact ligand coordinates.

## Dataset

- Input list: `protein-ligand-shape/input_list.txt`
- Molecule suffixes: `_r_u_shape` (receptor with shape), `_l_u` (ligand, unbound), `_shape_beads` (shape pseudoatoms)

## Scenarios

| Scenario | Description |
|---|---|
| `scenario_h24_unbound_unbound_shape` | Shape-guided docking using shape beads as ambiguous restraints |
| `scenario_h24_unbound_unbound_pharm` | Pharmacophore-guided docking using pharmacophore restraints |

## Workflow

```
topoaa → rigidbody → caprieval → seletop → flexref → emref → caprieval → ilrmsdmatrix → clustrmsd → seletopclusts → caprieval
```

## Notes

- `mol_fix_origin_1` and `mol_fix_origin_3: true` fix the receptor and shape beads in place during docking
- `mol_shape_3: true` flags the third molecule as shape pseudoatoms
- `w_vdw: 0.0` in rigidbody to avoid clashes with shape beads
- Ligand topology and parameters provided via `_ligand.param` / `_ligand.top`

## SLURM settings

- `partition: short`
- `ncores: 40`
- `max_concurrent: 10`
