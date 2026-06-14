# Protein-DNA Docking Benchmarks

This directory contains benchmarking scenarios for protein-DNA docking using HADDOCK3. Protein-DNA docking is significantly more challenging than protein-protein docking due to the polyanionic nature of DNA, its large conformational flexibility, and the need for specialised force field parameters to handle the nucleic acid backbone correctly.

These scenarios benchmark docking performance across three conformational states of the input structures — bound-bound, bound-unbound, and unbound-unbound — representing progressively harder docking challenges. DNA-specific HADDOCK3 parameters are applied throughout to properly model the electrostatic environment and structural flexibility of the DNA molecule.

## Dataset

- **Input list**: `prot-dna-input.txt` — lists each target with paths to protein chain(s) and DNA structure files
- **Molecule suffixes**: `_p1_b`, `_p2_b`, `_p3_b`, `_p4_b` (protein chains, bound), `_d_b` or `_d_u` (DNA, bound or unbound depending on scenario)
- **Restraint files**: `_b_ambig.tbl` — ambiguous restraints derived from the known binding interface

## DNA-Specific Force Field Parameters

All scenarios share a set of DNA-specific settings that override the defaults used for protein-protein docking:

- `epsilon: 78` — uses an aqueous dielectric constant to better model the highly charged DNA environment
- `dielec: cdie` — constant dielectric model (rather than distance-dependent), appropriate for nucleic acid electrostatics
- `w_desolv: 0` — desolvation energy term is disabled, as it is not well parameterised for DNA
- `dnarest_on: true` — enables DNA-specific positional restraints during flexible refinement to prevent unphysical distortions of the backbone
- `tadfactor: 4` — increases the torsion angle dynamics scaling factor during flexible refinement to allow larger backbone movements
- `temp_cool3_init: 300` — sets the initial temperature of the final cooling stage to 300 K for DNA flexibility

## Scenarios

### bound-bound

Both the protein and the DNA are provided in their bound (co-crystal) conformations. This represents the ideal case and serves as an upper-bound estimate for what the docking protocol can achieve, since no conformational change needs to be accommodated. Results from this scenario indicate the inherent scoring and sampling capability of the protocol when given optimal input structures.

**Workflow**: `topoaa → rigidbody (1000) → caprieval → seletop (200) → flexref → caprieval → mdref → caprieval → clustrmsd → seletopclusts → caprieval`

### bound-unbound

The protein is provided in its bound conformation but the DNA is in its free (unbound) form. This scenario is experimentally more realistic, as protein structures are often known from crystal structures of similar complexes while the free DNA structure is more readily available. It tests how well the protocol can accommodate the conformational change of the DNA upon protein binding.

**Workflow**: `topoaa → rigidbody (1000) → caprieval → seletop (200) → flexref → caprieval → emref → caprieval → clustfcc → seletopclusts → caprieval`

### unbound-unbound

Both protein and DNA are provided in their unbound (free solution) conformations. This is the most realistic and most difficult scenario, as both partners must undergo conformational adaptation to form the correct complex. It best reflects the real-world prediction challenge and is the primary scenario for benchmarking the general docking protocol.

**Workflow**: `topoaa → rigidbody (1000) → caprieval → seletop (200) → flexref → caprieval → mdref → caprieval → clustrmsd → seletopclusts → caprieval`

## Running

See [Usage/README.MD](../../Usage/README.MD) for path substitution, run commands, and SLURM configuration.
