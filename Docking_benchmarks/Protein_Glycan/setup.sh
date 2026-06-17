#!/bin/bash
 
# Download the protein-glycans dataset
git clone --depth 1 https://github.com/haddocking/protein-glycans.git || true
 
# Keep only pdb_files
rm -rf protein-glycans/{.git,analysis,cfg_files,data,LICENSE,README.md,example_pic.png}
 
# Create a `input-files.txt` file
ls `pwd`/protein-glycans/pdb_files/**/*.{pdb,tbl} | grep -v "ana_scripts\|matched\|cg" | sort > protein-glycan-input.txt
