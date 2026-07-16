#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# Download protein-protein BM5 benchmark dataset, converging to the pinned commit
clone_pinned https://github.com/haddocking/BM5-clean.git protein-protein-dataset "$BM5_CLEAN_REF"

# Create input list with paths to all PDB, restraint, and topology files
ls $(pwd)/protein-protein-dataset/HADDOCK-ready/**/*.{pdb,tbl,top,param} | grep -v "ana_scripts\|matched\|cg" | sort >bm5-input.txt
