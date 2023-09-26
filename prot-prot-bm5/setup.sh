#!/bin/bash

# Download the BM5 benchmark
git clone https://github.com/haddocking/BM5-clean.git || true

# Create a `input-files.txt` file
ls `pwd`/BM5-clean/HADDOCK-ready/**/*.{pdb,tbl,top,param} | grep -v "ana_scripts\|matched\|cg" | sort > bm5-input.txt