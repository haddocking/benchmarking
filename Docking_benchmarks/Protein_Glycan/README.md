# Protein-Glycan Docking Benchmarks

This directory contains benchmarking scenarios for protein-glycan docking using HADDOCK3. Glycans are carbohydrate chains attached to proteins and lipids, and they play critical roles in cell signalling, immune recognition, and pathogen-host interactions.

These benchmarks use topological interaction (TI) restraints derived from the glycan structure to guide docking, and evaluate multiple clustering strategies to identify the best-performing protocol for protein-glycan complexes.

## Dataset

- **Input list**: `prot-glycan-input.txt`
- **Molecule suffixes**: `_r_b` (receptor, bound), `_l_b` (glycan, bound), `_r_u` (receptor, unbound), `_l_u` (glycan, unbound), `_l_ensemble` (glycan conformational ensemble for scenario3)
- **Restraint files**: `_ti-aa.tbl` (true interface on both protein and glycan), `_tip-ap.tbl` (true interface on protein, glycan fully passive)
- **Reference structure**: `_analysis.pdb` — used for CAPRI evaluation

## About Topological Interaction Restraints

Topological interaction (TI) restraints encode the spatial relationships between glycan atoms and the protein surface based on the known geometry of the sugar rings and glycosidic bonds. The `ti-aa` variant uses all-atom (aa) representation for maximum geometric accuracy.

## Scenarios

### scenario1_bound_vdw_ti-aa

The simplest scenario: both the protein receptor and the glycan ligand are provided in their bound (co-crystal) conformations. TI restraints derived from the all-atom glycan structure are used alongside a van der Waals energy term (`w_vdw: 1`) during rigid-body docking.

### scenario2_unbound_vdw_tip_ap

The protein and glycan are both provided in their unbound conformations, making this a more realistic and challenging scenario. The restraints are switched from `ti-aa` to `tip-ap` (topological interaction point, all-atom with pharmacophoric features), which encode the preferred orientation of the glycan hydroxyl groups relative to the protein surface.

### scenario3_unbound_ens_vdw_tipap_clust

An extended version of scenario2 that incorporates ensemble-based sampling. Multiple conformations of the unbound glycan (provided as a structural ensemble) are used during the rigid-body stage to better represent the conformational space accessible to the free glycan.

## Running

See [Usage/README.MD](../../Usage/README.MD) for path substitution, run commands, and SLURM configuration.
