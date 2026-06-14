# Protein-Protein Docking Benchmarks

This directory contains benchmarking scenarios for protein-protein docking using the BM5 (Docking Benchmark 5) dataset. The benchmark evaluates both HADDOCK2.4 and HADDOCK3 docking protocols across a range of restraint strategies — from fully restrained docking using known interface information to completely ab initio docking without any prior knowledge of the binding site.

The BM5 dataset is a widely used gold standard for protein-protein docking benchmarks. It consists of 230 protein complexes with both bound and unbound structures available for each partner, enabling a rigorous assessment of docking performance under realistic conditions.

## Dataset

All scenarios share the same input dataset:

- **Input list**: `bm5-input.txt` — lists each target complex with paths to the unbound structures and associated restraint files
- **Molecule suffixes**: `_r_u` (receptor, unbound conformation), `_l_u` (ligand, unbound conformation)
- **Restraint files per target**: `_ambig.tbl` (ambiguous AIRs), `_restraint-bodies` (unambiguous body restraints), `_hbonds` (hydrogen bond restraints), `_ligand.param` / `_ligand.top` (ligand topology/parameters where applicable)

## Scenarios

### HADDOCK24_default

The default HADDOCK2.4 protocol for protein-protein docking. Ambiguous interaction restraints (AIRs) derived from experimental data or predicted interface residues are used to guide docking. The workflow follows the classic three-stage protocol: rigid-body docking to generate 1000 models, selection of the top 200, followed by semi-flexible refinement (flexref) and final water-mediated refinement (mdref). Clustering is performed using the FCC (Fraction of Common Contacts) method after the final refinement stage.

### HADDOCK24_default_5Aambig

Identical to the default HADDOCK2.4 protocol but with 5 Å ambiguous distance restraints applied in addition to the standard AIRs. This scenario tests whether softer, broader distance restraints can improve sampling at the interface and lead to better docking performance compared to the default setup.

### HADDOCK24_ab_initio

An ab initio docking scenario that operates without any knowledge of the binding interface. Instead of AIRs, random ambiguous interaction restraints (ranair) are used during the rigid-body stage to sample the entire surface. A larger pool of 1000 models is generated, and the top 400 are taken into refinement. Body restraints and hydrogen bond restraints are still applied to maintain the structural integrity of each partner. This scenario is the most challenging and tests docking performance in a blind prediction context.

### HADDOCK3_clustfcc

A HADDOCK3 protocol that introduces an early clustering step immediately after rigid-body docking — before semi-flexible refinement begins. By clustering the 1000 rigid-body models with FCC first and selecting representative structures, this approach reduces the risk of over-populating the refinement stage with near-duplicate poses and improves diversity in the final ensemble. Clustering is applied a second time after the full refinement to produce the final ranked results.

### HADDOCK3_ilrmsdclustering

Similar to HADDOCK3_clustfcc but uses interface-ligand RMSD (ilRMSD) matrix-based clustering instead of FCC at both clustering stages. ilRMSD clustering measures structural similarity in terms of the interface geometry rather than contact overlap, which can capture different aspects of pose diversity and may rank solutions differently compared to FCC-based clustering.

## Running

See [Usage/README.MD](../../Usage/README.MD) for path substitution, run commands, and SLURM configuration.
