#!/bin/bash

#Download and extract protein-peptide dataset
git clone https://github.com/haddocking/protein-peptide protein-peptide-dataset

#rename ligand ensemble files from *_l_u_ensemble.pdb to *_l_u.pdb so they match the input-list pattern
find protein-peptide-dataset -name "*_l_u_ensemble.pdb" \
  -exec bash -c 'mv "$0" "${0/_l_u_ensemble/_l_u}"' {} \;

ls $(pwd)/protein-peptide-dataset/**/*.{pdb,tbl} \
| grep -v "ana_scripts\|matched\|cg" \
| grep -E "_r_u\.pdb$|_l_u\.pdb$|_b_ambig\.tbl$|_target\.pdb$" \
| sort > protein-peptide-input.txt
