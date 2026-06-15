#!/bin/bash

# Download protein-protein BM5 benchmark dataset
git clone https://github.com/haddocking/BM5-clean.git || true

# Create input list with paths to all PDB, restraint, and topology files
ls `pwd`/BM5-clean/HADDOCK-ready/**/*.{pdb,tbl,top,param} | grep -v "ana_scripts\|matched\|cg" | sort > bm5-input.txt
