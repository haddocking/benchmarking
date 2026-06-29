#!/bin/bash

#Download and extract protein-peptide dataset
git clone https://github.com/haddocking/protein-peptide protein-peptide-dataset

ls $(pwd)/protein-peptide-dataset/**/*.{pdb,tbl} \
| grep -v "ana_scripts\|matched\|cg" \
| grep -E "_r_u\.pdb$|_l_u\.pdb$|_b_ambig\.tbl$|_target\.pdb$" \
| sort > protein-peptide-input.txt
