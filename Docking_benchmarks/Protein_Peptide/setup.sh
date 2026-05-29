#!/bin/bash



#Download and extract protein-peptide dataset
git clone https://github.com/haddocking/protein-peptide

#make a output directory

mkdir -p HADDOCK-Prot-peptide

find protein-peptide -name "*_l_u_ensemble.pdb" \
  -exec bash -c 'mv "$0" "${0/_l_u_ensemble/_l_u}"' {} \;

#create a input-files.txt
#ls $(pwd)/protein-peptide/**/*.{pdb,tbl} | grep -v "ana_scripts\|matched\|cg" | sort > prot-peptide-input.txt

ls $(pwd)/protein-peptide/**/*.{pdb,tbl} \
| grep -v "ana_scripts\|matched\|cg" \
| grep -E "_r_u\.pdb$|_l_u\.pdb$|_b_ambig\.tbl$|_target\.pdb$" \
| sort > prot-peptide-input.txt
