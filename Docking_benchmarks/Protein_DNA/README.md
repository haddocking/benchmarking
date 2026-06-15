# Protein-DNA Docking Benchmarks

This directory contains benchmarking scenarios for protein-DNA docking using HADDOCK3. Protein-DNA docking is significantly more challenging than protein-protein docking due to the polyanionic nature of DNA, its large conformational flexibility, and the need for specialised force field parameters to handle the nucleic acid backbone correctly.

These scenarios benchmark docking performance across three conformational states of the input structures — bound-bound, bound-unbound, and unbound-unbound — representing progressively harder docking challenges. DNA-specific HADDOCK3 parameters are applied throughout to properly model the electrostatic environment and structural flexibility of the DNA molecule.

## Dataset

- **Input list**: `prot-dna-input.txt` — lists each target with paths to protein chain(s), DNA structure files, restraint files, and the reference complex

The molecule suffixes and restraint files differ per scenario:

| Scenario | Protein suffixes | DNA suffix | Restraints |
|---|---|---|---|
| bound-bound | `_p1_b` … `_p4_b` | `_d_b` (co-crystal DNA) | `_b_ambig.tbl` |
| bound-unbound | `_p1_b` … `_p4_b` | `_d_u` (ideal B-form DNA) | `_b_ambig.tbl` |
| unbound-unbound | `_p1_u` … `_p4_u` | `_d_u` (ideal B-form DNA) | `_u_ambig.tbl` |

Not all targets have up to four protein chains — `_p3` and `_p4` are only present where the complex requires them.

`_d_u` is a computationally generated DNA structure built from the sequence, not taken from a crystal structure. Where the unbound protein is from an NMR ensemble, `setup.sh` concatenates the individual model files (e.g. `1HJC_p1_u_1.pdb`, `_2.pdb`) into a single multi-model PDB (`1HJC_p1_u.pdb`). HADDOCK3 automatically detects the MODEL records and samples from the ensemble during docking.

## Scenarios

### bound-bound

Both the protein and the DNA are provided in their bound (co-crystal) conformations. This represents the ideal case and serves as an upper-bound estimate for what the docking protocol can achieve, since no conformational change needs to be accommodated. Results from this scenario indicate the inherent scoring and sampling capability of the protocol when given optimal input structures.

### bound-unbound

The protein is provided in its bound conformation but the DNA is in its free (unbound) form. This scenario is experimentally more realistic, as protein structures are often known from crystal structures of similar complexes while the free DNA structure is more readily available. It tests how well the protocol can accommodate the conformational change of the DNA upon protein binding.

### unbound-unbound

Both protein and DNA are provided in their unbound (free solution) conformations. This is the most realistic and most difficult scenario, as both partners must undergo conformational adaptation to form the correct complex. It best reflects the real-world prediction challenge and is the primary scenario for benchmarking the general docking protocol.

## Running

See [Usage/README.MD](../../Usage/README.MD) for path substitution, run commands, and SLURM configuration.
