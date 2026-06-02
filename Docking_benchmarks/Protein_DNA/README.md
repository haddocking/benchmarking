# Protein-DNA Docking Benchmarks

Benchmarking scenarios for protein-DNA docking using HADDOCK3. DNA-specific force field settings are applied (constant dielectric, desolvation disabled, DNA restraints enabled).

## Dataset

- Input list: `prot-dna-input.txt`
- Molecule suffixes: `_p1_b`, `_p2_b`, `_p3_b`, `_p4_b` (protein chains), `_d_b` (DNA)

## Scenarios

| Scenario | Description |
|---|---|
| `scenario_bound-bound` | Both protein and DNA in bound conformation |
| `scenario_bound-unbound` | Protein in bound, DNA in unbound conformation |
| `scenario_unbound-unbound` | Both protein and DNA in unbound conformation |

## Workflow

```
topoaa → rigidbody → caprieval → seletop → flexref → mdref → clustrmsd → seletopclusts → caprieval
```

## Notes

- DNA-specific parameters: `epsilon: 78`, `dielec: cdie`, `w_desolv: 0`, `dnarest_on: true`
- `tadfactor: 4` and `temp_cool3_init: 300` set in flexref for DNA flexibility
- `watersteps: 750` used in mdref water refinement stage

## SLURM settings

- `partition: short`
- `ncores: 40`
- `max_concurrent: 10`
