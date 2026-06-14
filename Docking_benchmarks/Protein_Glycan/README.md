# Protein-Glycan Docking Benchmarks

This directory contains benchmarking scenarios for protein-glycan docking using HADDOCK3. Glycans are carbohydrate chains attached to proteins and lipids, and they play critical roles in cell signalling, immune recognition, and pathogen-host interactions. Despite their biological importance, protein-glycan docking remains one of the most challenging problems in structural biology due to the extreme conformational flexibility of glycan chains, their complex branching topology, and the relatively weak and diffuse nature of the protein-carbohydrate interaction interface.

These benchmarks use topological interaction (TI) restraints derived from the glycan structure to guide docking, and evaluate multiple clustering strategies to identify the best-performing protocol for protein-glycan complexes.

## Dataset

- **Input list**: `prot-glycan-input.txt`
- **Molecule suffixes**: `_r_b` (receptor, bound conformation), `_l_b` (glycan ligand, bound) for bound scenarios; `_r_u` / `_l_u` for unbound scenarios
- **Restraint files**: `_ti-aa.tbl` — topological interaction restraints derived from all-atom glycan geometry

## About Topological Interaction Restraints

Topological interaction (TI) restraints encode the spatial relationships between glycan atoms and the protein surface based on the known geometry of the sugar rings and glycosidic bonds. They are more informative than simple distance-based AIRs for glycans because they capture the directional preferences imposed by the rigid pyranose rings and the dihedral angles of the glycosidic linkages. The `ti-aa` variant uses all-atom (aa) representation for maximum geometric accuracy.

## Scenarios

### scenario1_bound_vdw_ti-aa

The simplest scenario: both the protein receptor and the glycan ligand are provided in their bound (co-crystal) conformations. TI restraints derived from the all-atom glycan structure are used alongside a van der Waals energy term (`w_vdw: 1`) during rigid-body docking. After an initial RMSD-based clustering of the 1000 rigid-body poses (selecting the top 50 clusters of up to 20 models each), the top structures enter semi-flexible refinement (`flexref`). A second, tighter RMSD clustering (2.5 Å cutoff, average linkage) is then applied to produce the final ranked ensemble. HETATM records are retained throughout evaluation to ensure glycan atoms are correctly included in the CAPRI assessment.

**Workflow**: `topoaa → rigidbody (1000, w_vdw=1) → caprieval → ilrmsdmatrix → clustrmsd (maxclust 50) → seletopclusts → caprieval → flexref → caprieval → ilrmsdmatrix → clustrmsd (2.5 Å) → seletopclusts → caprieval`

### scenario2_unbound_vdw_tip_ap

The protein and glycan are both provided in their unbound conformations, making this a more realistic and challenging scenario. The restraints are switched from `ti-aa` to `tip-ap` (topological interaction point, all-atom with pharmacophoric features), which encode the preferred orientation of the glycan hydroxyl groups relative to the protein surface. The protocol otherwise mirrors scenario1, with VdW-guided rigid-body sampling followed by two rounds of clustering and one round of flexible refinement.

**Workflow**: `topoaa → rigidbody (1000, w_vdw=1) → caprieval → ilrmsdmatrix → clustrmsd → seletopclusts → caprieval → flexref → caprieval → ilrmsdmatrix → clustrmsd → seletopclusts → caprieval`

### scenario3_unbound_ens_vdw_tipap_clust

An extended version of scenario2 that incorporates ensemble-based sampling. Multiple conformations of the unbound glycan (provided as a structural ensemble) are used during the rigid-body stage to better represent the conformational space accessible to the free glycan. This scenario is designed to test whether ensemble input can compensate for the conformational selection challenge inherent in glycan docking, where the free ligand may need to adopt a conformation not well represented by a single unbound structure.

**Workflow**: `topoaa → rigidbody (ensemble, w_vdw=1) → caprieval → ilrmsdmatrix → clustrmsd → seletopclusts → caprieval → flexref → caprieval → ilrmsdmatrix → clustrmsd → seletopclusts → caprieval`

## Running

See [Usage/README.MD](../../Usage/README.MD) for path substitution, run commands, and SLURM configuration.
