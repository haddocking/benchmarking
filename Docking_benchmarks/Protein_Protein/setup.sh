#!/bin/bash

# Download protein-protein BM5 benchmark dataset
git clone https://github.com/haddocking/BM5-clean.git protein-protein-dataset || true

# Keep only the HADDOCK-ready directory; everything else in the cloned repo
find protein-protein-dataset/ -mindepth 1 -maxdepth 1 ! -name 'HADDOCK-ready' -exec rm -rf {} +

# Create input list with paths to all PDB, restraint, and topology files
ls `pwd`/protein-protein-dataset/HADDOCK-ready/**/*.{pdb,tbl,top,param} | grep -v "ana_scripts\|matched\|cg" | sort > bm5-input.txt
